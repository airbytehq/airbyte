# Config Database: connectors and definitions

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
