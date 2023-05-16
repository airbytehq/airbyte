# A snowflake user with no create schema privilege.

resource "snowflake_role" "no_create_schema_privilege" {
  provider = snowflake.securityadmin
  name = "ROLE_WITHOUT_CREATE_SCHEMA_PRIVILEGE"
}

resource "random_password" "password" {
  length           = 64
  special          = true
}

resource "snowflake_user" "no_create_schema_privilege" {
  provider = snowflake.securityadmin
  name = "INTEGRATION_TEST_DESTINATION_NO_CREATE_SCHEMA_PRIVILEGE"
  password = random_password.password.result
  default_role = snowflake_role.airbyte.name
  default_warehouse = snowflake_warehouse.airbyte_warehouse.name
  default_namespace = snowflake_database.airbyte_database.name
}

resource "snowflake_role_grants" "no_create_schema_privilege" {
  provider = snowflake.securityadmin
  role_name = snowflake_role.no_create_schema_privilege.name

  users = [
    snowflake_user.no_create_schema_privilege.name
  ]
}

resource "snowflake_database_grant" "no_create_schema_privilege" {
  provider = snowflake.sysadmin
  database_name = snowflake_database.airbyte_database.name
  # NB: not ownership
  privilege = "USAGE"
  roles = [
    snowflake_role.airbyte.name,
    "NESH_01",
    "NESH_ROLE",
    "TEST_STAGING_ROLE",
  ]
}

resource "snowflake_schema" "no_create_schema_privilege" {
  provider = snowflake.sysadmin
  database = snowflake_database.airbyte_database.name
  name = "INTEGRATION_TEST_DESTINATION_NO_CREATE_SCHEMA_PRIVILEGE"
}

resource "google_secret_manager_secret" "destination_snowflake_no_create_schema_privilege" {
  secret_id = "SECRET_DESTINATION_SNOWFLAKE_NO_CREATE_SCHEMA_PRIVILEGE"

  labels = {
    connector = "destination-snowflake"
    filename = "no_create_schema_privilege"
  }

  replication {
    user_managed {
      replicas {
        location = "us-central1"
      }
      replicas {
        location = "us-east1"
      }
    }
  }
}

resource "google_secret_manager_secret_version" "destination_snowflake_no_create_schema_privilege" {
  secret = google_secret_manager_secret.destination_snowflake_no_create_schema_privilege.id
  secret_data = jsonencode({
    host = local.snowflake_host
    role = snowflake_role.no_create_schema_privilege.name
    warehouse = snowflake_warehouse.airbyte_warehouse.name
    database = snowflake_database.airbyte_database.name
    schema = snowflake_schema.no_create_schema_privilege.name
    username = snowflake_user.no_create_schema_privilege.name
    credentials = {
      password = random_password.password.result
    }
    loading_method = {
      method = "Internal Staging"
    }
  })
}
