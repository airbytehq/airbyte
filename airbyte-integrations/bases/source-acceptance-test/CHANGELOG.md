# Changelog

## 0.1.6
Add configurable validation of schema for all records in BasicRead test: https://github.com/airbytehq/airbyte/pull/4345
The validation is ON by default. 
To disable validation for the source you need to set `validate_schema: off` in the config file.

## 0.1.5
Add configurable timeout for the acceptance tests: https://github.com/airbytehq/airbyte/pull/4296
