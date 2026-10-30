# Airbyte Databases Data Catalog

## Config Database

### `active_declarative_manifest`

| Column Name           | Datatype  | Description                                           |
| --------------------- | --------- | ----------------------------------------------------- |
| actor_definition_id   | UUID      | Primary key. References the `actor_definition` table. |
| version              | BIGINT    | Version of the manifest.                              |
| created_at           | TIMESTAMP | Timestamp when the record was created.               |
| updated_at           | TIMESTAMP | Timestamp when the record was last updated.          |

#### Indexes and Constraints

- Primary Key: (`actor_definition_id`)
- Foreign Key: `actor_definition_id` references `actor_definition(id)`

---

### `actor`

| Column Name            | Datatype     | Description                                             |
| ---------------------- | ------------ | ------------------------------------------------------- |
| id                     | UUID         | Primary key. Unique identifier for the actor.          |
| workspace_id           | UUID         | Foreign key referencing the `workspace` table.         |
| actor_definition_id    | UUID         | Foreign key referencing `actor_definition` table.      |
| name                   | VARCHAR(256) | Name of the actor.                                     |
| configuration          | JSONB        | Configuration JSON blob specific to the actor.         |
| actor_type             | ENUM         | Indicates whether the actor is a source or destination.|
| tombstone              | BOOLEAN      | Soft delete flag.                                      |
| created_at             | TIMESTAMP    | Timestamp when the record was created.                 |
| updated_at             | TIMESTAMP    | Timestamp when the record was last updated.            |
| resource_requirements  | JSONB        | Defines resource requirements for the actor.           |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `workspace_id` references `workspace(id)`
- Foreign Key: `actor_definition_id` references `actor_definition(id)`
- Index: `actor_definition_id_idx` on (`actor_definition_id`)
- Index: `actor_workspace_id_idx` on (`workspace_id`)

---

### `actor_catalog`

| Column Name   | Datatype    | Description                                     |
| ------------- | ----------- | ----------------------------------------------- |
| id            | UUID        | Primary key. Unique identifier for the catalog. |
| catalog       | JSONB       | JSON representation of the catalog.             |
| catalog_hash  | VARCHAR(32) | Hash of the catalog for quick comparison.       |
| created_at    | TIMESTAMP   | Timestamp when the record was created.          |
| modified_at   | TIMESTAMP   | Timestamp when the record was last modified.    |

#### Indexes and Constraints

- Primary Key: (`id`)
- Index: `actor_catalog_catalog_hash_id_idx` on (`catalog_hash`)

---

### `actor_catalog_fetch_event`

| Column Name        | Datatype     | Description                                              |
| ------------------ | ------------ | -------------------------------------------------------- |
| id                 | UUID         | Primary key. Unique identifier for the fetch event.      |
| actor_catalog_id   | UUID         | Foreign key referencing `actor_catalog(id)`.             |
| actor_id           | UUID         | Foreign key referencing `actor(id)`.                     |
| config_hash        | VARCHAR(32)  | Hash of the configuration at the time of the fetch.      |
| actor_version      | VARCHAR(256) | Version of the actor definition when the fetch occurred. |
| created_at         | TIMESTAMP    | Timestamp when the record was created.                   |
| modified_at        | TIMESTAMP    | Timestamp when the record was last modified.             |

#### `Indexes and Constraints`

- Primary Key: (`id`)
- Foreign Key: `actor_catalog_id` references `actor_catalog(id)`
- Foreign Key: `actor_id` references `actor(id)`
- Index: `actor_catalog_fetch_event_actor_catalog_id_idx` on (`actor_catalog_id`)
- Index: `actor_catalog_fetch_event_actor_id_idx` on (`actor_id`)

---

### `actor_definition`

| Column Name                     | Datatype     | Description                                              |
| -------------------------------- | ------------ | -------------------------------------------------------- |
| id                               | UUID         | Primary key. Unique identifier for the actor definition. |
| name                             | VARCHAR(256) | Name of the connector.                                   |
| icon                             | VARCHAR(256) | Icon for the connector.                                 |
| actor_type                       | ENUM         | Indicates whether the actor is a source or destination. |
| source_type                      | ENUM         | Source category (e.g., API, Database).                  |
| created_at                       | TIMESTAMP    | Timestamp when the record was created.                   |
| updated_at                       | TIMESTAMP    | Timestamp when the record was last modified.             |
| tombstone                        | BOOLEAN      | Soft delete flag.                                        |
| resource_requirements            | JSONB        | Defines default resource requirements.                   |
| public                           | BOOLEAN      | Determines if the definition is publicly available.      |
| custom                           | BOOLEAN      | Indicates if the connector is user-defined.              |
| max_seconds_between_messages     | INT          | Maximum allowed seconds between messages.                |
| default_version_id               | UUID         | Foreign key referencing `actor_definition_version(id)`.  |
| icon_url                         | VARCHAR(256) | URL of the icon image.                                   |
| metrics                          | JSONB        | Metadata about the connector.                            |
| enterprise                       | BOOLEAN      | Whether the connector is part of the enterprise edition.|

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `default_version_id` references `actor_definition_version(id)`

---

### `actor_definition_breaking_change`

| Column Name                     | Datatype     | Description                                                 |
| -------------------------------- | ------------ | ----------------------------------------------------------- |
| actor_definition_id              | UUID         | Foreign key referencing `actor_definition(id)`.              |
| version                          | VARCHAR(256) | Version of the breaking change.                             |
| migration_documentation_url      | VARCHAR(256) | URL linking to migration documentation.                     |
| upgrade_deadline                 | DATE         | Deadline for upgrading to the new version.                   |
| message                          | TEXT         | Description of the breaking change.                         |
| created_at                       | TIMESTAMP    | Timestamp when the record was created.                      |
| updated_at                       | TIMESTAMP    | Timestamp when the record was last modified.                |
| scoped_impact                    | JSONB        | JSON object describing the impact scope.                    |
| deadline_action                   | VARCHAR(256) | Action required before the deadline.                        |

#### Indexes and Constraints

- Primary Key: (`actor_definition_id`, `version`)
- Foreign Key: `actor_definition_id` references `actor_definition(id)`

---

### `actor_definition_config_injection`

| Column Name         | Datatype    | Description                                     |
| ------------------ | ----------- | ----------------------------------------------- |
| json_to_inject    | JSONB       | JSON configuration to inject.                   |
| injection_path    | VARCHAR     | Path where the injection applies.               |
| actor_definition_id | UUID        | Foreign key referencing `actor_definition(id)`.|
| created_at        | TIMESTAMP   | Timestamp when the record was created.          |
| updated_at        | TIMESTAMP   | Timestamp when the record was last modified.    |

#### Indexes and Constraints

- Primary Key: (`actor_definition_id`, `injection_path`)
- Foreign Key: `actor_definition_id` references `actor_definition(id)`

---

### `actor_definition_version`

| Column Name         | Datatype     | Description                                  |
| ------------------- | ------------ | -------------------------------------------- |
| id                 | UUID         | Primary key. Unique identifier for the version. |
| actor_definition_id | UUID         | Foreign key referencing `actor_definition(id)`. |
| created_at         | TIMESTAMP    | Timestamp when the record was created.       |
| updated_at         | TIMESTAMP    | Timestamp when the record was last modified. |
| documentation_url  | VARCHAR(256) | Documentation URL for this version.         |
| docker_repository | VARCHAR(256) | Docker repository name.                      |
| docker_image_tag  | VARCHAR(256) | Docker image tag for this version.           |
| spec              | JSONB        | Specification JSON blob.                     |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `actor_definition_id` references `actor_definition(id)`
- Unique Constraint: `actor_definition_id, docker_image_tag`

---

### `actor_definition_workspace_grant`

| Column Name          | Datatype | Description                                    |
| ------------------- | -------- | ---------------------------------------------- |
| actor_definition_id | UUID     | Foreign key referencing `actor_definition(id)`. |
| workspace_id       | UUID     | Foreign key referencing `workspace(id)`.       |
| scope_id          | UUID     | Scope identifier.                             |

#### Indexes and Constraints

- Unique Constraint: `actor_definition_id, scope_id, scope_type`

---

### `actor_oauth_parameter`

| Column Name          | Datatype  | Description                                    |
| ------------------- | --------- | ---------------------------------------------- |
| id                 | UUID      | Primary key. Unique identifier.               |
| workspace_id       | UUID      | Foreign key referencing `workspace(id)`.       |
| actor_definition_id | UUID      | Foreign key referencing `actor_definition(id)`. |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `workspace_id` references `workspace(id)`
- Foreign Key: `actor_definition_id` references `actor_definition(id)`

---

### `airbyte_configs_migrations`

| Column Name     | Datatype      | Description                                     |
| --------------- | ------------- | ----------------------------------------------- |
| installed_rank  | INT           | Primary key. Rank of the installed migration.   |
| version        | VARCHAR(50)    | Version number of the migration.                |
| description    | VARCHAR(200)   | Description of the migration.                   |
| type          | VARCHAR(20)     | Type of migration.                              |
| script        | VARCHAR(1000)   | Script executed for the migration.              |
| checksum      | INT             | Checksum of the migration script.               |
| installed_by  | VARCHAR(100)    | User who installed the migration.               |
| installed_on  | TIMESTAMP       | Timestamp when the migration was installed.     |
| execution_time | INT            | Time taken to execute the migration.            |
| success       | BOOLEAN         | Indicates whether the migration was successful. |

#### Indexes and Constraints
- Primary Key: (`installed_rank`)

---

### `application`

| Column Name    | Datatype  | Description                                         |
| -------------- | --------- | --------------------------------------------------- |
| id             | UUID      | Primary key. Unique identifier for the application. |
| user_id       | UUID      | Foreign key referencing `user(id)`.                 |
| name           | VARCHAR   | Name of the application.                            |
| client_id     | VARCHAR   | Client ID for authentication.                       |
| client_secret | VARCHAR   | Secret key for authentication.                      |
| created_at    | TIMESTAMP | Timestamp when the record was created.              |

#### Indexes and Constraints
- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`

---

### `auth_refresh_token`

| Column Name  | Datatype  | Description                                     |
| ------------ | --------- | ----------------------------------------------- |
| value        | VARCHAR   | Primary key. Refresh token value.               |
| session_id   | VARCHAR   | ID of the session associated with the token.    |
| revoked      | BOOLEAN   | Indicates whether the token has been revoked.   |
| created_at   | TIMESTAMP | Timestamp when the record was created.          |
| updated_at   | TIMESTAMP | Timestamp when the record was last modified.    |

#### Indexes and Constraints
- Primary Key: (`value`)
- Unique Constraint: (`session_id`, `value`)

---

### `auth_user`

| Column Name    | Datatype  | Description                                       |
| -------------- | --------- | ------------------------------------------------- |
| id             | UUID      | Primary key. Unique identifier for the auth user. |
| user_id       | UUID      | Foreign key referencing `user(id)`.               |
| auth_user_id  | VARCHAR   | ID of the authenticated user.                     |
| auth_provider | ENUM      | Authentication provider used.                     |
| created_at    | TIMESTAMP | Timestamp when the record was created.            |
| updated_at    | TIMESTAMP | Timestamp when the record was last modified.      |

#### Indexes and Constraints
- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`
- Unique Constraint: (`auth_user_id`, `auth_provider`)

---

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

### `connector_builder_project`

| Column Name                     | Datatype  | Description                                       |
| -------------------------------- | --------- | ------------------------------------------------- |
| id                               | UUID      | Primary key. Unique identifier for the project.   |
| workspace_id                     | UUID      | Foreign key referencing `workspace(id)`.         |
| name                             | VARCHAR   | Name of the connector project.                    |
| manifest_draft                   | JSONB     | JSON draft of the connector manifest.             |
| actor_definition_id              | UUID      | Foreign key referencing `actor_definition(id)`.   |
| tombstone                        | BOOLEAN   | Indicates if the project is deleted.              |
| created_at                       | TIMESTAMP | Timestamp when the record was created.            |
| updated_at                       | TIMESTAMP | Timestamp when the record was last modified.      |
| testing_values                   | JSONB     | JSON containing test values for the connector.    |
| base_actor_definition_version_id | UUID      | Foreign key referencing `actor_definition_version(id)`. |
| contribution_pull_request_url    | VARCHAR   | URL for the contribution PR.                      |
| contribution_actor_definition_id | UUID      | Foreign key referencing `actor_definition(id)`.   |
| components_file_content          | TEXT      | Raw content of component files.                   |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `workspace_id` references `workspace(id)`
- Foreign Key: `actor_definition_id` references `actor_definition(id)`
- Foreign Key: `base_actor_definition_version_id` references `actor_definition_version(id)`
- Foreign Key: `contribution_actor_definition_id` references `actor_definition(id)`
- Index: `connector_builder_project_workspace_idx` on (`workspace_id`)

---

### `connector_rollout`

| Column Name                  | Datatype  | Description                                      |
| ---------------------------- | --------- | ------------------------------------------------ |
| id                            | UUID      | Primary key. Unique identifier for the rollout. |
| actor_definition_id           | UUID      | Foreign key referencing `actor_definition(id)`. |
| release_candidate_version_id  | UUID      | Foreign key referencing `actor_definition_version(id)`. |
| initial_version_id            | UUID      | Foreign key referencing `actor_definition_version(id)`. |
| state                         | VARCHAR   | Current state of the rollout.                    |
| initial_rollout_pct           | INT       | Initial rollout percentage.                      |
| current_target_rollout_pct    | INT       | Current target rollout percentage.               |
| final_target_rollout_pct      | INT       | Final target rollout percentage.                 |
| has_breaking_changes          | BOOLEAN   | Indicates if the rollout has breaking changes.   |
| max_step_wait_time_mins       | INT       | Maximum wait time between rollout steps.         |
| updated_by                    | UUID      | Foreign key referencing `user(id)`.              |
| created_at                    | TIMESTAMP | Timestamp when the rollout started.              |
| updated_at                    | TIMESTAMP | Timestamp when the record was last modified.     |
| completed_at                  | TIMESTAMP | Timestamp when the rollout was completed.        |
| expires_at                    | TIMESTAMP | Timestamp when the rollout expires.              |
| error_msg                     | VARCHAR   | Error message if the rollout failed.             |
| failed_reason                 | VARCHAR   | Reason for failure.                              |
| rollout_strategy              | VARCHAR   | Strategy used for the rollout.                   |
| workflow_run_id               | VARCHAR   | Workflow run identifier.                         |
| paused_reason                 | VARCHAR   | Reason for pausing the rollout.                  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `actor_definition_id` references `actor_definition(id)`
- Foreign Key: `release_candidate_version_id` references `actor_definition_version(id)`
- Foreign Key: `initial_version_id` references `actor_definition_version(id)`
- Foreign Key: `updated_by` references `user(id)`
- Unique Index: `actor_definition_id_state_unique_idx` on `actor_definition_id`
    - Condition: (`state` in ['errored', 'finalizing', 'in_progress', 'initialized', 'paused', 'workflow_started'])

---

### `dataplane`

| Column Name        | Datatype  | Description                                      |
| ------------------ | --------- | ------------------------------------------------ |
| id                | UUID      | Primary key. Unique identifier for the dataplane. |
| dataplane_group_id | UUID      | Foreign key referencing `dataplane_group(id)`.   |
| name              | VARCHAR   | Name of the dataplane.                           |
| enabled           | BOOLEAN   | Indicates if the dataplane is enabled.           |
| created_at        | TIMESTAMP | Timestamp when the record was created.           |
| updated_at        | TIMESTAMP | Timestamp when the record was last modified.     |
| updated_by        | UUID      | Foreign key referencing `user(id)`.              |
| tombstone         | BOOLEAN   | Indicates if the record is deleted.              |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `dataplane_group_id` references `dataplane_group(id)`
- Foreign Key: `updated_by` references `user(id)`
- Unique Constraint: (`dataplane_group_id`, `name`)

---

### `dataplane_group`

| Column Name      | Datatype  | Description                                      |
| --------------- | --------- | ------------------------------------------------ |
| id             | UUID      | Primary key. Unique identifier for the group.    |
| organization_id | UUID      | Foreign key referencing `organization(id)`.      |
| name           | VARCHAR   | Name of the dataplane group.                     |
| enabled        | BOOLEAN   | Indicates if the group is enabled.               |
| created_at     | TIMESTAMP | Timestamp when the record was created.           |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.     |
| updated_by     | UUID      | Foreign key referencing `user(id)`.              |
| tombstone      | BOOLEAN   | Indicates if the record is deleted.              |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
- Foreign Key: `updated_by` references `user(id)`
- Unique Constraint: (`organization_id`, `name`)

---

### `declarative_manifest`

| Column Name          | Datatype  | Description                                      |
| -------------------- | --------- | ------------------------------------------------ |
| actor_definition_id  | UUID      | Foreign key referencing `actor_definition(id)`.  |
| description         | VARCHAR   | Description of the manifest.                     |
| manifest           | JSONB     | JSON representation of the manifest.            |
| spec               | JSONB     | JSON specification for the manifest.            |
| version            | BIGINT    | Version number of the manifest.                 |
| created_at         | TIMESTAMP | Timestamp when the record was created.           |

#### Indexes and Constraints

- Primary Key: (`actor_definition_id`, `version`)

---

### `declarative_manifest_image_version`

| Column Name    | Datatype  | Description                          |
| ------------- | --------- | ------------------------------------ |
| major_version | INT       | Primary key. Major version number.  |
| image_version | VARCHAR   | Version of the image.               |
| created_at    | TIMESTAMP | Timestamp when the record was created. |
| updated_at    | TIMESTAMP | Timestamp when the record was last modified. |
| image_sha     | VARCHAR   | SHA checksum of the image.          |

#### Indexes and Constraints

- Primary Key: (`major_version`)

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

### `organization`

| Column Name  | Datatype  | Description                                      |
| ------------ | --------- | ------------------------------------------------ |
| id          | UUID      | Primary key. Unique identifier for the organization. |
| name        | VARCHAR   | Name of the organization.                         |
| user_id     | UUID      | Foreign key referencing `user(id)`.               |
| email       | VARCHAR   | Contact email for the organization.              |
| created_at  | TIMESTAMP | Timestamp when the record was created.            |
| updated_at  | TIMESTAMP | Timestamp when the record was last modified.      |
| tombstone   | BOOLEAN   | Indicates if the organization is deleted.         |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`

---

### `organization_email_domain`

| Column Name      | Datatype  | Description                                     |
| ---------------- | --------- | ----------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the record.  |
| organization_id | UUID      | Foreign key referencing `organization(id)`.     |
| email_domain   | VARCHAR   | Email domain associated with the organization.  |
| created_at     | TIMESTAMP | Timestamp when the record was created.          |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
- Unique Constraint: (`organization_id`, `email_domain`)
- Index: `organization_email_domain_organization_id_idx` on (`organization_id`)

---

### `organization_payment_config`

| Column Name               | Datatype  | Description                                    |
| ------------------------- | --------- | ---------------------------------------------- |
| organization_id           | UUID      | Primary key. Unique identifier for the organization payment configuration. |
| payment_provider_id       | VARCHAR   | Payment provider ID.                          |
| payment_status            | ENUM      | Status of the organization's payment.        |
| grace_period_end_at       | TIMESTAMP | End timestamp for the grace period.          |
| usage_category_override   | ENUM      | Override for usage category.                 |
| created_at                | TIMESTAMP | Timestamp when the record was created.       |
| updated_at                | TIMESTAMP | Timestamp when the record was last modified. |
| subscription_status       | ENUM      | Status of the organization's subscription.   |

#### Indexes and Constraints

- Primary Key: (`organization_id`)
- Unique Constraint: (`payment_provider_id`)
- Foreign Key: `organization_id` references `organization(id)`
- Index: `organization_payment_config_payment_status_idx` on (`payment_status`)
- Index: `organization_payment_config_payment_provider_id_idx` on (`payment_provider_id`)

---

### `permission`

| Column Name        | Datatype  | Description                                    |
| ------------------ | --------- | ---------------------------------------------- |
| id                | UUID      | Primary key. Unique identifier for the permission. |
| user_id          | UUID      | Foreign key referencing `user(id)`.            |
| workspace_id     | UUID      | Foreign key referencing `workspace(id)`.       |
| created_at       | TIMESTAMP | Timestamp when the record was created.        |
| updated_at       | TIMESTAMP | Timestamp when the record was last modified.  |
| organization_id  | UUID      | Foreign key referencing `organization(id)`.    |
| permission_type  | ENUM      | Type of permission assigned.                   |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`
- Foreign Key: `workspace_id` references `workspace(id)`
- Foreign Key: `organization_id` references `organization(id)`
- Unique Constraint: (`user_id`, `organization_id`)
- Unique Constraint: (`user_id`, `workspace_id`)
- Index: `permission_organization_id_idx` on (`organization_id`)
- Index: `permission_workspace_id_idx` on (`workspace_id`)

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

### `scoped_configuration`

| Column Name      | Datatype  | Description                                    |
| --------------- | --------- | ---------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the scoped configuration. |
| key            | VARCHAR   | Configuration key.                            |
| resource_type  | ENUM      | Type of resource associated with the configuration. |
| resource_id    | UUID      | Identifier of the associated resource.        |
| scope_type     | ENUM      | Type of scope (e.g., workspace, organization). |
| scope_id       | UUID      | Identifier for the scope of the configuration. |
| value          | VARCHAR   | Value of the configuration.                   |
| description    | TEXT      | Description of the configuration setting.     |
| reference_url  | VARCHAR   | URL reference for more information.           |
| origin_type    | ENUM      | Type of origin for the configuration setting. |
| origin        | VARCHAR   | Source of the configuration setting.          |
| expires_at     | DATE      | Expiration date of the configuration.         |
| created_at     | TIMESTAMP | Timestamp when the record was created.        |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Unique Constraint: (`key`, `resource_type`, `resource_id`, `scope_type`, `scope_id`)

---

### `secret_persistence_config`

| Column Name                           | Datatype  | Description                                       |
| ------------------------------------- | --------- | ------------------------------------------------- |
| id                                    | UUID      | Primary key. Unique identifier for secret persistence configuration. |
| scope_id                              | UUID      | Identifier for the scope of the secret.          |
| scope_type                            | ENUM      | Scope type (`organization`, `workspace`, etc.).  |
| secret_persistence_config_coordinate | VARCHAR   | Coordinate for secret persistence configuration. |
| secret_persistence_type               | ENUM      | Type of secret persistence method.               |
| created_at                            | TIMESTAMP | Timestamp when the record was created.           |
| updated_at                            | TIMESTAMP | Timestamp when the record was last modified.     |

#### Indexes and Constraints

- Primary Key: (`id`)
- Unique Constraint: (`scope_id`, `scope_type`)

---

### `sso_config`

| Column Name       | Datatype  | Description                                    |
| ---------------- | --------- | ---------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the SSO configuration. |
| organization_id | UUID      | Foreign key referencing `organization(id)`.    |
| keycloak_realm | VARCHAR   | Keycloak realm associated with the organization. |
| created_at     | TIMESTAMP | Timestamp when the record was created.         |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.   |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
- Unique Constraint: (`keycloak_realm`)
- Unique Constraint: (`organization_id`)
- Index: `sso_config_keycloak_realm_idx` on (`keycloak_realm`)
- Index: `sso_config_organization_id_idx` on (`organization_id`)

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

### `user`

| Column Name           | Datatype  | Description                                      |
| --------------------- | --------- | ------------------------------------------------ |
| id                   | UUID      | Primary key. Unique identifier for the user.     |
| name                 | VARCHAR   | Name of the user.                                |
| default_workspace_id | UUID      | Foreign key referencing `workspace(id)`.        |
| status              | ENUM      | Status of the user account.                     |
| company_name        | VARCHAR   | Name of the company associated with the user.   |
| email               | VARCHAR   | Email address of the user.                      |
| news                | BOOLEAN   | Whether the user subscribes to newsletters.     |
| ui_metadata         | JSONB     | UI metadata associated with the user.           |
| created_at          | TIMESTAMP | Timestamp when the record was created.          |
| updated_at          | TIMESTAMP | Timestamp when the record was last modified.    |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `default_workspace_id` references `workspace(id)`
- Unique Constraint: (`email`)
- Index: `user_email_idx` on (`email`)
- Unique Index: `user_email_unique_key` on `lower(email)`

---

### `user_invitation`

| Column Name       | Datatype  | Description                                         |
| ---------------- | --------- | --------------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the invitation.  |
| invite_code     | VARCHAR   | Unique code for the invitation.                     |
| inviter_user_id | UUID      | Foreign key referencing `user(id)`.                 |
| invited_email   | VARCHAR   | Email of the invited user.                          |
| permission_type | ENUM      | Type of permission granted to the invited user.    |
| status         | ENUM      | Status of the invitation (`pending`, `accepted`, etc.). |
| created_at     | TIMESTAMP | Timestamp when the record was created.              |
| updated_at     | TIMESTAMP | Timestamp when the record was last modified.        |
| scope_id       | UUID      | Scope ID for the invitation.                        |
| scope_type     | ENUM      | Type of scope (`organization`, `workspace`, etc.).  |
| accepted_by_user_id | UUID  | Foreign key referencing `user(id)`.                 |
| expires_at     | TIMESTAMP | Expiration timestamp of the invitation.             |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `inviter_user_id` references `user(id)`
- Foreign Key: `accepted_by_user_id` references `user(id)`
- Unique Constraint: (`invite_code`)
- Index: `user_invitation_invite_code_idx` on (`invite_code`)
- Index: `user_invitation_invited_email_idx` on (`invited_email`)
- Index: `user_invitation_scope_id_index` on (`scope_id`)
- Index: `user_invitation_scope_type_and_scope_id_index` on (`scope_type`, `scope_id`)
- Index: `user_invitation_accepted_by_user_id_index` on (`accepted_by_user_id`)
- Index: `user_invitation_expires_at_index` on (`expires_at`)

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

### `workspace`

| Column Name               | Datatype  | Description                                   |
| ------------------------ | --------- | --------------------------------------------- |
| id                      | UUID      | Primary key. Unique identifier for the workspace. |
| customer_id             | UUID      | Customer associated with the workspace.      |
| name                    | VARCHAR   | Name of the workspace.                       |
| slug                    | VARCHAR   | Slug identifier for the workspace.           |
| email                   | VARCHAR   | Contact email for the workspace.             |
| initial_setup_complete  | BOOLEAN   | Whether the initial setup is complete.       |
| anonymous_data_collection | BOOLEAN | Whether anonymous data collection is enabled. |
| send_newsletter         | BOOLEAN   | Whether the user is subscribed to newsletters. |
| send_security_updates   | BOOLEAN   | Whether security updates are sent.           |
| display_setup_wizard    | BOOLEAN   | Whether the setup wizard should be displayed. |
| tombstone               | BOOLEAN   | Whether the workspace is deleted.            |
| notifications           | JSONB     | Notification settings.                        |
| first_sync_complete    | BOOLEAN   | Whether the first sync has completed.        |
| feedback_complete      | BOOLEAN   | Whether feedback collection is completed.    |
| created_at             | TIMESTAMP | Timestamp when the record was created.       |
| updated_at             | TIMESTAMP | Timestamp when the record was last modified. |
| geography              | ENUM      | Geography associated with the workspace.     |
| webhook_operation_configs | JSONB  | Webhook operation configurations.            |
| notification_settings  | JSONB     | Notification settings for the workspace.     |
| organization_id        | UUID      | Foreign key referencing `organization(id)`.  |

#### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`

---

### `workspace_service_account`

| Column Name            | Datatype  | Description                                      |
| ---------------------- | --------- | ------------------------------------------------ |
| workspace_id          | UUID      | Foreign key referencing `workspace(id)`.       |
| service_account_id    | VARCHAR   | Service account ID.                             |
| service_account_email | VARCHAR   | Email associated with the service account.      |
| json_credential      | JSONB     | JSON blob storing credentials.                  |
| hmac_key             | JSONB     | JSON blob storing HMAC keys.                    |
| created_at           | TIMESTAMP | Timestamp when the record was created.          |
| updated_at           | TIMESTAMP | Timestamp when the record was last modified.    |

#### Indexes and Constraints

- Primary Key: (`workspace_id`, `service_account_id`)
- Foreign Key: `workspace_id` references `workspace(id)`



## Jobs Database

### `jobs`

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

#### Indexes & Constraints

- Primary Key: `id`
- Indexes:
    - `jobs_config_type_idx` → (`config_type`)
    - `jobs_scope_idx` → (`scope`)
    - `jobs_status_idx` → (`status`)
    - `jobs_updated_at_idx` → (`updated_at`)
    - `scope_created_at_idx` → (`scope`, `created_at` DESC)
    - `scope_non_terminal_status_idx` → (`scope`, `status`) (only for non-terminal statuses: not `failed`, `succeeded`, or `cancelled`)

---

### `attempts`

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

#### Indexes & Constraints

- Primary Key: `id`
- Foreign Key: `job_id` → `jobs(id)`
- Indexes:
    - `attempts_status_idx` → (`status`)
    - `job_attempt_idx` → (`job_id`, `attempt_number`) (Unique)

---

### `airbyte_metadata`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `key`           | `varchar(255)` | Primary key, uniquely identifies a metadata key. |
| `value`         | `varchar(255)` | Value associated with the key. |

#### Indexes & Constraints

- Primary Key: `key`

---

### `airbyte_jobs_migrations`

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

#### Indexes & Constraints

- Primary Key: `installed_rank`
- Indexes:
    - `airbyte_jobs_migrations_s_idx` → (`success`)

---

### `normalization_summaries`

| Column Name  | Datatype  | Description |
|------------------|--------------|----------------|
| `id`            | `uuid`        | Primary key, uniquely identifies a normalization summary. |
| `attempt_id`    | `bigint`      | Foreign key to `attempts(id)`. |
| `start_time`    | `timestamp(6) with time zone` | Start time of the normalization process. |
| `end_time`      | `timestamp(6) with time zone` | End time of the normalization process. |
| `failures`      | `jsonb`       | JSON blob containing failure details. |
| `created_at`    | `timestamp(6) with time zone` | Timestamp when the summary was created. |
| `updated_at`    | `timestamp(6) with time zone` | Timestamp when the summary was last updated. |

#### Indexes & Constraints

- Primary Key: `id`
- Foreign Key: `attempt_id` → `attempts(id)`
- Indexes:
    - `normalization_summary_attempt_id_idx` → (`attempt_id`)
