# Note

- The config persistence used to read from the definition files under the `STANDARD_SOURCE_DEFINITION` and `STANDARD_DESTINATION_DEFINITION` directories. However, it reads from the [seeds](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed) directly now.
- These deprecated definition files are not deleted because they are needed by old Airbyte versions.
