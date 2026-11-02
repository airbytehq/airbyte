# Jobs Database

## `jobs`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `id`            | `bigint`      | Primary key, uniquely identifies a job. |
| `config_type`   | `job_config_type` | Type of job (`sync`, `reset`). |
| `scope`         | `varchar(255)` | Identifier for the connection or scope of the job. |
| `config`        | `jsonb`       | JSON blob containing job configuration. |
| `status`        | `job_status`  | Current status of the job (`running`, `failed`, `succeeded`, etc.). |
| `started_at`    | `timestamp(6) with time zone` | Timestamp when the job started. |
| `created_at`    | `timestamp(6) with time zone` | Timestamp when the job was created. |
| `updated_at`    | `timestamp(6) with time zone` | Timestamp when the job was last updated. |
| `metadata`      | `jsonb`       | JSON blob containing metadata for the job. |
| `is_scheduled`  | `boolean`     | Whether the job was scheduled automatically (default: `true`). |

### Indexes & Constraints

- Primary Key: `id`
- Indexes:
    - `jobs_config_type_idx` → (`config_type`)
    - `jobs_scope_idx` → (`scope`)
    - `jobs_status_idx` → (`status`)
    - `jobs_updated_at_idx` → (`updated_at`)
    - `scope_created_at_idx` → (`scope`, `created_at` DESC)
    - `scope_non_terminal_status_idx` → (`scope`, `status`) (only for non-terminal statuses: not `failed`, `succeeded`, or `cancelled`)

---

## `attempts`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `id`            | `bigint`      | Primary key, uniquely identifies an attempt. |
| `job_id`        | `bigint`      | Foreign key to `jobs(id)`, linking the attempt to a job. |
| `attempt_number` | `int`         | Number of the attempt for a given job. |
| `log_path`      | `varchar(255)` | Path where logs for this attempt are stored. |
| `output`        | `jsonb`       | JSON blob containing the attempt's output details. |
| `status`        | `attempt_status` | Status of the attempt (`running`, `failed`, `succeeded`). |
| `created_at`    | `timestamp(6) with time zone` | Timestamp when the attempt was created. |
| `updated_at`    | `timestamp(6) with time zone` | Timestamp when the attempt was last updated. |
| `ended_at`      | `timestamp(6) with time zone` | Timestamp when the attempt ended. |
| `failure_summary` | `jsonb`       | JSON blob containing failure reason details. |
| `processing_task_queue` | `varchar(255)` | Task queue identifier for processing. |
| `attempt_sync_config` | `jsonb`   | JSON blob for sync configuration. |

### Indexes & Constraints

- Primary Key: `id`
- Foreign Key: `job_id` → `jobs(id)`
- Indexes:
    - `attempts_status_idx` → (`status`)
    - `job_attempt_idx` → (`job_id`, `attempt_number`) (Unique)

---

## `airbyte_metadata`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `key`           | `varchar(255)` | Primary key, uniquely identifies a metadata key. |
| `value`         | `varchar(255)` | Value associated with the key. |

### Indexes & Constraints

- Primary Key: `key`

---

## `airbyte_jobs_migrations`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `installed_rank` | `int`        | Primary key, rank of migration execution. |
| `version`       | `varchar(50)` | Version number of the migration. |
| `description`   | `varchar(200)` | Description of the migration. |
| `type`         | `varchar(20)`  | Type of migration. |
| `script`       | `varchar(1000)` | Name of the migration script. |
| `checksum`     | `int`         | Checksum of the migration script. |
| `installed_by` | `varchar(100)` | User who installed the migration. |
| `installed_on` | `timestamp(6)` | Timestamp when migration was installed. |
| `execution_time` | `int`        | Execution time in milliseconds. |
| `success`      | `boolean`     | Whether the migration succeeded. |

### Indexes & Constraints

- Primary Key: `installed_rank`
- Indexes:
    - `airbyte_jobs_migrations_s_idx` → (`success`)

---

## `normalization_summaries`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `id`            | `uuid`        | Primary key, uniquely identifies a normalization summary. |
| `attempt_id`    | `bigint`      | Foreign key to `attempts(id)`. |
| `start_time`    | `timestamp(6) with time zone` | Start time of the normalization process. |
| `end_time`      | `timestamp(6) with time zone` | End time of the normalization process. |
| `failures`      | `jsonb`       | JSON blob containing failure details. |
| `created_at`    | `timestamp(6) with time zone` | Timestamp when the summary was created. |
| `updated_at`    | `timestamp(6) with time zone` | Timestamp when the summary was last updated. |

### Indexes & Constraints

- Primary Key: `id`
- Foreign Key: `attempt_id` → `attempts(id)`
- Indexes:
    - `normalization_summary_attempt_id_idx` → (`attempt_id`)
