# Config Database: organizations, workspaces, and access

## `airbyte_configs_migrations`

| Column Name    | Datatype      | Description                                     |
| -------------- | ------------- | ----------------------------------------------- |
| installed_rank | INT           | Primary key. Rank of the installed migration.   |
| version        | VARCHAR(50)   | Version number of the migration.                |
| description    | VARCHAR(200)  | Description of the migration.                   |
| type           | VARCHAR(20)   | Type of migration.                              |
| script         | VARCHAR(1000) | Script executed for the migration.              |
| checksum       | INT           | Checksum of the migration script.               |
| installed_by   | VARCHAR(100)  | User who installed the migration.               |
| installed_on   | TIMESTAMP     | Timestamp when the migration was installed.     |
| execution_time | INT           | Time taken to execute the migration.            |
| success        | BOOLEAN       | Indicates whether the migration was successful. |

### Indexes and Constraints

- Primary Key: (`installed_rank`)

---

## `application`

| Column Name   | Datatype  | Description                                         |
| ------------- | --------- | --------------------------------------------------- |
| id            | UUID      | Primary key. Unique identifier for the application. |
| user_id       | UUID      | Foreign key referencing `user(id)`.                 |
| name          | VARCHAR   | Name of the application.                            |
| client_id     | VARCHAR   | Client ID for authentication.                       |
| client_secret | VARCHAR   | Secret key for authentication.                      |
| created_at    | TIMESTAMP | Timestamp when the record was created.              |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`

---

## `auth_refresh_token`

| Column Name | Datatype  | Description                                   |
| ----------- | --------- | --------------------------------------------- |
| value       | VARCHAR   | Primary key. Refresh token value.             |
| session_id  | VARCHAR   | ID of the session associated with the token.  |
| revoked     | BOOLEAN   | Indicates whether the token has been revoked. |
| created_at  | TIMESTAMP | Timestamp when the record was created.        |
| updated_at  | TIMESTAMP | Timestamp when the record was last modified.  |

### Indexes and Constraints

- Primary Key: (`value`)
- Unique Constraint: (`session_id`, `value`)

---

## `auth_user`

| Column Name   | Datatype  | Description                                       |
| ------------- | --------- | ------------------------------------------------- |
| id            | UUID      | Primary key. Unique identifier for the auth user. |
| user_id       | UUID      | Foreign key referencing `user(id)`.               |
| auth_user_id  | VARCHAR   | ID of the authenticated user.                     |
| auth_provider | ENUM      | Authentication provider used.                     |
| created_at    | TIMESTAMP | Timestamp when the record was created.            |
| updated_at    | TIMESTAMP | Timestamp when the record was last modified.      |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`
- Unique Constraint: (`auth_user_id`, `auth_provider`)

---

## `dataplane`

| Column Name        | Datatype  | Description                                       |
| ------------------ | --------- | ------------------------------------------------- |
| id                 | UUID      | Primary key. Unique identifier for the dataplane. |
| dataplane_group_id | UUID      | Foreign key referencing `dataplane_group(id)`.    |
| name               | VARCHAR   | Name of the dataplane.                            |
| enabled            | BOOLEAN   | Indicates if the dataplane is enabled.            |
| created_at         | TIMESTAMP | Timestamp when the record was created.            |
| updated_at         | TIMESTAMP | Timestamp when the record was last modified.      |
| updated_by         | UUID      | Foreign key referencing `user(id)`.               |
| tombstone          | BOOLEAN   | Indicates if the record is deleted.               |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `dataplane_group_id` references `dataplane_group(id)`
- Foreign Key: `updated_by` references `user(id)`
- Unique Constraint: (`dataplane_group_id`, `name`)

---

## `dataplane_diagnostic`

| Column Name     | Datatype     | Description                                                                     |
| --------------- | ------------ | ------------------------------------------------------------------------------- |
| id              | UUID         | Primary key. Unique identifier for the diagnostic.                              |
| dataplane_id    | UUID         | Required. Foreign key referencing `dataplane(id)`.                              |
| organization_id | UUID         | Required. Identifier for the organization.                                      |
| diagnostic_kind | VARCHAR(256) | Required. Kind of diagnostic check.                                             |
| target_id       | UUID         | Required. Identifier for the tested target.                                     |
| status          | VARCHAR(256) | Required. Status of the diagnostic.                                             |
| checked_at      | TIMESTAMPTZ  | Required. Timestamp when the launcher ran the check.                            |
| created_at      | TIMESTAMPTZ  | Required. Timestamp when the record was created. Defaults to `NOW()`.           |
| updated_at      | TIMESTAMPTZ  | Required. Timestamp when Airbyte last received the result. Defaults to `NOW()`. |
| error_code      | VARCHAR(256) | Nullable. Error code for the diagnostic.                                        |
| error_message   | TEXT         | Nullable. Error message for the diagnostic.                                     |
| observation     | JSONB        | Nullable. Observation from the diagnostic.                                      |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `dataplane_id` references `dataplane(id)` ON DELETE CASCADE
- Unique Constraint: (`dataplane_id`, `diagnostic_kind`, `target_id`)

---

## `dataplane_group`

| Column Name     | Datatype  | Description                                   |
| --------------- | --------- | --------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the group. |
| organization_id | UUID      | Foreign key referencing `organization(id)`.   |
| name            | VARCHAR   | Name of the dataplane group.                  |
| enabled         | BOOLEAN   | Indicates if the group is enabled.            |
| created_at      | TIMESTAMP | Timestamp when the record was created.        |
| updated_at      | TIMESTAMP | Timestamp when the record was last modified.  |
| updated_by      | UUID      | Foreign key referencing `user(id)`.           |
| tombstone       | BOOLEAN   | Indicates if the record is deleted.           |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
- Foreign Key: `updated_by` references `user(id)`
- Unique Constraint: (`organization_id`, `name`)

---

## `organization`

| Column Name       | Datatype  | Description                                                                                                            |
| ----------------- | --------- | ---------------------------------------------------------------------------------------------------------------------- |
| id                | UUID      | Primary key. Unique identifier for the organization.                                                                   |
| name              | VARCHAR   | Name of the organization.                                                                                              |
| user_id           | UUID      | Foreign key referencing `user(id)`.                                                                                    |
| email             | VARCHAR   | Contact email for the organization.                                                                                    |
| created_at        | TIMESTAMP | Timestamp when the record was created.                                                                                 |
| updated_at        | TIMESTAMP | Timestamp when the record was last modified.                                                                           |
| tombstone         | BOOLEAN   | Indicates if the organization is deleted.                                                                              |
| onboarding_status | VARCHAR   | Nullable text. Status in the Cloud onboarding flow. `NULL` means the organization never went through Cloud onboarding. |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`

---

## `organization_email_domain`

| Column Name     | Datatype  | Description                                    |
| --------------- | --------- | ---------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the record. |
| organization_id | UUID      | Foreign key referencing `organization(id)`.    |
| email_domain    | VARCHAR   | Email domain associated with the organization. |
| created_at      | TIMESTAMP | Timestamp when the record was created.         |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
- Unique Constraint: (`organization_id`, `email_domain`)
- Index: `organization_email_domain_organization_id_idx` on (`organization_id`)

---

## `organization_payment_config`

| Column Name             | Datatype  | Description                                                                |
| ----------------------- | --------- | -------------------------------------------------------------------------- |
| organization_id         | UUID      | Primary key. Unique identifier for the organization payment configuration. |
| payment_provider_id     | VARCHAR   | Payment provider ID.                                                       |
| payment_status          | ENUM      | Status of the organization's payment.                                      |
| grace_period_end_at     | TIMESTAMP | End timestamp for the grace period.                                        |
| usage_category_override | ENUM      | Override for usage category.                                               |
| created_at              | TIMESTAMP | Timestamp when the record was created.                                     |
| updated_at              | TIMESTAMP | Timestamp when the record was last modified.                               |
| subscription_status     | ENUM      | Status of the organization's subscription.                                 |

### Indexes and Constraints

- Primary Key: (`organization_id`)
- Unique Constraint: (`payment_provider_id`)
- Foreign Key: `organization_id` references `organization(id)`
- Index: `organization_payment_config_payment_status_idx` on (`payment_status`)
- Index: `organization_payment_config_payment_provider_id_idx` on (`payment_provider_id`)

---

## `permission`

| Column Name     | Datatype  | Description                                        |
| --------------- | --------- | -------------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the permission. |
| user_id         | UUID      | Foreign key referencing `user(id)`.                |
| workspace_id    | UUID      | Foreign key referencing `workspace(id)`.           |
| created_at      | TIMESTAMP | Timestamp when the record was created.             |
| updated_at      | TIMESTAMP | Timestamp when the record was last modified.       |
| organization_id | UUID      | Foreign key referencing `organization(id)`.        |
| permission_type | ENUM      | Type of permission assigned.                       |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `user_id` references `user(id)`
- Foreign Key: `workspace_id` references `workspace(id)`
- Foreign Key: `organization_id` references `organization(id)`
- Unique Constraint: (`user_id`, `organization_id`)
- Unique Constraint: (`user_id`, `workspace_id`)
- Index: `permission_organization_id_idx` on (`organization_id`)
- Index: `permission_workspace_id_idx` on (`workspace_id`)

---

## `scoped_configuration`

| Column Name   | Datatype  | Description                                                  |
| ------------- | --------- | ------------------------------------------------------------ |
| id            | UUID      | Primary key. Unique identifier for the scoped configuration. |
| key           | VARCHAR   | Configuration key.                                           |
| resource_type | ENUM      | Type of resource associated with the configuration.          |
| resource_id   | UUID      | Identifier of the associated resource.                       |
| scope_type    | ENUM      | Type of scope (e.g., workspace, organization).               |
| scope_id      | UUID      | Identifier for the scope of the configuration.               |
| value         | VARCHAR   | Value of the configuration.                                  |
| description   | TEXT      | Description of the configuration setting.                    |
| reference_url | VARCHAR   | URL reference for more information.                          |
| origin_type   | ENUM      | Type of origin for the configuration setting.                |
| origin        | VARCHAR   | Source of the configuration setting.                         |
| expires_at    | DATE      | Expiration date of the configuration.                        |
| created_at    | TIMESTAMP | Timestamp when the record was created.                       |
| updated_at    | TIMESTAMP | Timestamp when the record was last modified.                 |

### Indexes and Constraints

- Primary Key: (`id`)
- Unique Constraint: (`key`, `resource_type`, `resource_id`, `scope_type`, `scope_id`)

---

## `secret_persistence_config`

| Column Name                          | Datatype  | Description                                                          |
| ------------------------------------ | --------- | -------------------------------------------------------------------- |
| id                                   | UUID      | Primary key. Unique identifier for secret persistence configuration. |
| scope_id                             | UUID      | Identifier for the scope of the secret.                              |
| scope_type                           | ENUM      | Scope type (`organization`, `workspace`, etc.).                      |
| secret_persistence_config_coordinate | VARCHAR   | Coordinate for secret persistence configuration.                     |
| secret_persistence_type              | ENUM      | Type of secret persistence method.                                   |
| created_at                           | TIMESTAMP | Timestamp when the record was created.                               |
| updated_at                           | TIMESTAMP | Timestamp when the record was last modified.                         |

### Indexes and Constraints

- Primary Key: (`id`)
- Unique Constraint: (`scope_id`, `scope_type`)

---

## `sso_config`

| Column Name     | Datatype  | Description                                               |
| --------------- | --------- | --------------------------------------------------------- |
| id              | UUID      | Primary key. Unique identifier for the SSO configuration. |
| organization_id | UUID      | Foreign key referencing `organization(id)`.               |
| keycloak_realm  | VARCHAR   | Keycloak realm associated with the organization.          |
| created_at      | TIMESTAMP | Timestamp when the record was created.                    |
| updated_at      | TIMESTAMP | Timestamp when the record was last modified.              |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
- Unique Constraint: (`keycloak_realm`)
- Unique Constraint: (`organization_id`)
- Index: `sso_config_keycloak_realm_idx` on (`keycloak_realm`)
- Index: `sso_config_organization_id_idx` on (`organization_id`)

---

## `user`

| Column Name          | Datatype  | Description                                   |
| -------------------- | --------- | --------------------------------------------- |
| id                   | UUID      | Primary key. Unique identifier for the user.  |
| name                 | VARCHAR   | Name of the user.                             |
| default_workspace_id | UUID      | Foreign key referencing `workspace(id)`.      |
| status               | ENUM      | Status of the user account.                   |
| company_name         | VARCHAR   | Name of the company associated with the user. |
| email                | VARCHAR   | Email address of the user.                    |
| news                 | BOOLEAN   | Whether the user subscribes to newsletters.   |
| ui_metadata          | JSONB     | UI metadata associated with the user.         |
| created_at           | TIMESTAMP | Timestamp when the record was created.        |
| updated_at           | TIMESTAMP | Timestamp when the record was last modified.  |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `default_workspace_id` references `workspace(id)`
- Unique Constraint: (`email`)
- Index: `user_email_idx` on (`email`)
- Unique Index: `user_email_unique_key` on `lower(email)`

---

## `user_invitation`

| Column Name         | Datatype  | Description                                             |
| ------------------- | --------- | ------------------------------------------------------- |
| id                  | UUID      | Primary key. Unique identifier for the invitation.      |
| invite_code         | VARCHAR   | Unique code for the invitation.                         |
| inviter_user_id     | UUID      | Foreign key referencing `user(id)`.                     |
| invited_email       | VARCHAR   | Email of the invited user.                              |
| permission_type     | ENUM      | Type of permission granted to the invited user.         |
| status              | ENUM      | Status of the invitation (`pending`, `accepted`, etc.). |
| created_at          | TIMESTAMP | Timestamp when the record was created.                  |
| updated_at          | TIMESTAMP | Timestamp when the record was last modified.            |
| scope_id            | UUID      | Scope ID for the invitation.                            |
| scope_type          | ENUM      | Type of scope (`organization`, `workspace`, etc.).      |
| accepted_by_user_id | UUID      | Foreign key referencing `user(id)`.                     |
| expires_at          | TIMESTAMP | Expiration timestamp of the invitation.                 |

### Indexes and Constraints

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

## `workspace`

| Column Name               | Datatype  | Description                                       |
| ------------------------- | --------- | ------------------------------------------------- |
| id                        | UUID      | Primary key. Unique identifier for the workspace. |
| customer_id               | UUID      | Customer associated with the workspace.           |
| name                      | VARCHAR   | Name of the workspace.                            |
| slug                      | VARCHAR   | Slug identifier for the workspace.                |
| email                     | VARCHAR   | Contact email for the workspace.                  |
| initial_setup_complete    | BOOLEAN   | Whether the initial setup is complete.            |
| anonymous_data_collection | BOOLEAN   | Whether anonymous data collection is enabled.     |
| send_newsletter           | BOOLEAN   | Whether the user is subscribed to newsletters.    |
| send_security_updates     | BOOLEAN   | Whether security updates are sent.                |
| display_setup_wizard      | BOOLEAN   | Whether the setup wizard should be displayed.     |
| tombstone                 | BOOLEAN   | Whether the workspace is deleted.                 |
| notifications             | JSONB     | Notification settings.                            |
| first_sync_complete       | BOOLEAN   | Whether the first sync has completed.             |
| feedback_complete         | BOOLEAN   | Whether feedback collection is completed.         |
| created_at                | TIMESTAMP | Timestamp when the record was created.            |
| updated_at                | TIMESTAMP | Timestamp when the record was last modified.      |
| geography                 | ENUM      | Geography associated with the workspace.          |
| webhook_operation_configs | JSONB     | Webhook operation configurations.                 |
| notification_settings     | JSONB     | Notification settings for the workspace.          |
| organization_id           | UUID      | Foreign key referencing `organization(id)`.       |

### Indexes and Constraints

- Primary Key: (`id`)
- Foreign Key: `organization_id` references `organization(id)`
