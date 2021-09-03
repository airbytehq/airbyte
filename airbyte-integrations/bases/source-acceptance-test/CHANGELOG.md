# Changelog

## 0.1.17
Fix serialize function for acceptance-tests: https://github.com/airbytehq/airbyte/pull/5738

## 0.1.16
Fix for flake8-ckeck for acceptance-tests: https://github.com/airbytehq/airbyte/pull/5785

## 0.1.15
Add detailed logging for acceptance tests: https://github.com/airbytehq/airbyte/pull/5392

## 0.1.14
Fix for NULL datetime in MySQL format (i.e. 0000-00-00): https://github.com/airbytehq/airbyte/pull/4465

## 0.1.13
Replace `validate_output_from_all_streams` with `empty_streams` param: https://github.com/airbytehq/airbyte/pull/4897

## 0.1.12
Improve error message when data mismatches schema: https://github.com/airbytehq/airbyte/pull/4753

## 0.1.11
Fix error in the naming of method `test_match_expected` for class `TestSpec`.

## 0.1.10
Add validation of input config.json against spec.json.

## 0.1.9
Add configurable validation of schema for all records in BasicRead test: https://github.com/airbytehq/airbyte/pull/4345
The validation is ON by default. 
To disable validation for the source you need to set `validate_schema: off` in the config file.

## 0.1.8
Fix cursor_path to support nested and absolute paths: https://github.com/airbytehq/airbyte/pull/4552

## 0.1.7
Add: `test_spec` additionally checks if Dockerfile has `ENV AIRBYTE_ENTRYPOINT` defined and equal to space_joined `ENTRYPOINT`

## 0.1.6
Add test whether PKs present and not None if `source_defined_primary_key` defined: https://github.com/airbytehq/airbyte/pull/4140

## 0.1.5
Add configurable timeout for the acceptance tests: https://github.com/airbytehq/airbyte/pull/4296

