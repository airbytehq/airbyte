locals {
  snowflake_host = "gz45853.us-east-2.aws.snowflakecomputing.com"
}

resource "snowflake_role" "airbyte" {
  provider = snowflake.securityadmin
  name     = "AIRBYTE_ROLE"
}

resource "snowflake_role_grants" "sysadmin_grants" {
  provider  = snowflake.securityadmin
  role_name = snowflake_role.airbyte.name
  roles     = ["SYSADMIN"]
}

# resource "snowflake_user" "airbyte_user" {
#   provider = snowflake.securityadmin
#   name = "INTEGRATION_TEST_USER_DESTINATION"
#   password = random_password.password.result
#   default_role = snowflake_role.airbyte.name
#   default_warehouse = snowflake_warehouse.airbyte_warehouse.name
# }

# resource "snowflake_role_grants" "user_grant" {
#   provider = snowflake.securityadmin
#   role_name = snowflake_role.airbyte.name

#   users = [
#     snowflake_user.airbyte_user.name
#   ]
# }

resource "snowflake_warehouse" "airbyte_warehouse" {
  provider       = snowflake.sysadmin
  name           = "AIRBYTE_WAREHOUSE"
  warehouse_size = "xsmall"
  warehouse_type = "STANDARD"
  auto_suspend   = 3600
  auto_resume    = true
  # This has a weird default of 8 and query acceleration can not be enabled, setting to 0 allows progress when
  # Feature is disabled
  query_acceleration_max_scale_factor = 0
}

resource "snowflake_database" "airbyte_database" {
  provider = snowflake.sysadmin
  name     = "AIRBYTE_DATABASE"
}

resource "snowflake_warehouse_grant" "ab_warehouse_grant" {
  provider       = snowflake.sysadmin
  warehouse_name = snowflake_warehouse.airbyte_warehouse.name
  privilege      = "USAGE"
  roles = [
    snowflake_role.airbyte.name,
    # No idea what these are, but terraform plan says they exist
    "NESH_01",
    "NESH_ROLE",
    "SYSADMIN",
    "SYSADMIN_NATALIE",
    "TEST_STAGING_ROLE",
    "TEST_TESH_ROLE",
    "TEST_TESH_ROLE2",
  ]
}

resource "snowflake_database_grant" "ab_db_grant" {
  provider      = snowflake.sysadmin
  database_name = snowflake_database.airbyte_database.name
  privilege     = "OWNERSHIP"
  roles = [
    snowflake_role.airbyte.name,
    # No idea what this is, but terraform plan says it exists
    "NESH_01"
  ]
}

resource "snowflake_schema" "airbyte_schema" {
  provider = snowflake.sysadmin
  database = snowflake_database.airbyte_database.name
  name     = "AIRBYTE_SCHEMA"
}

resource "snowflake_schema_grant" "ab_aschema_grant" {
  provider      = snowflake.sysadmin
  database_name = snowflake_database.airbyte_database.name
  schema_name   = snowflake_schema.airbyte_schema.name
  privilege     = "OWNERSHIP"
  roles = [
    snowflake_role.airbyte.name
  ]
}
