# airbyte-json-validation

This module contains shared Java code for validating JSON objects.

## Key Files
* `JsonSchemaValidator.java` is the main entrypoint into this library, defining convenience methods for validation.
* `ConfigSchemaValidator.java` is additional sugar to make it easy to validate objects whose schemas are defined in `ConfigSchema`.
