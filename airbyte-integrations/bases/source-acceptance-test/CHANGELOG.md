# Changelog

## 0.1.46
Fix `test_oneof_usage` test: [#9861](https://github.com/airbytehq/airbyte/pull/9861)

## 0.1.45
Check for not allowed keywords `allOf`, `not` in connectors schema: [#9851](https://github.com/airbytehq/airbyte/pull/9851)

## 0.1.44
Fix incorrect name of `primary_keys` attribute: [#9768](https://github.com/airbytehq/airbyte/pull/9768)

## 0.1.43
`TestFullRefresh` test can compare records using PKs: [#9768](https://github.com/airbytehq/airbyte/pull/9768)

## 0.1.36
Add assert that `spec.json` file does not have any `$ref` in it: [#8842](https://github.com/airbytehq/airbyte/pull/8842)

## 0.1.32
Add info about skipped failed tests in `/test` command message on GitHub: [#8691](https://github.com/airbytehq/airbyte/pull/8691)

## 0.1.31
Take `ConfiguredAirbyteCatalog` from discover command by default

## 0.1.30
Validate if each field in a stream has appeared at least once in some record.

## 0.1.29
Add assert that output catalog does not have any `$ref` in it

## 0.1.28
Print stream name when incremental sync tests fail

## 0.1.27
Add ignored fields for full refresh test (unit tests)

## 0.1.26
Add ignored fields for full refresh test

## 0.1.25
Fix incorrect nested structures compare.

## 0.1.24
Improve message about errors in the stream's schema: [#6934](https://github.com/airbytehq/airbyte/pull/6934)

## 0.1.23
Fix incorrect auth init flow check defect.

## 0.1.22
Fix checking schemas with root `$ref` keyword

## 0.1.21
Fix rootObject oauth init parameter check

## 0.1.20
Add oauth init flow parameter verification for spec.

## 0.1.19
Assert a non-empty overlap between the fields present in the record and the declared json schema.

## 0.1.18
Fix checking date-time format against nullable field.

## 0.1.17
Fix serialize function for acceptance-tests: [#5738](https://github.com/airbytehq/airbyte/pull/5738)

## 0.1.16
Fix for flake8-ckeck for acceptance-tests: [#5785](https://github.com/airbytehq/airbyte/pull/5785)

## 0.1.15
Add detailed logging for acceptance tests: [5392](https://github.com/airbytehq/airbyte/pull/5392)

## 0.1.14
Fix for NULL datetime in MySQL format (i.e. `0000-00-00`): [#4465](https://github.com/airbytehq/airbyte/pull/4465)

## 0.1.13
Replace `validate_output_from_all_streams` with `empty_streams` param: [#4897](https://github.com/airbytehq/airbyte/pull/4897)

## 0.1.12
Improve error message when data mismatches schema: [#4753](https://github.com/airbytehq/airbyte/pull/4753)

## 0.1.11
Fix error in the naming of method `test_match_expected` for class `TestSpec`.

## 0.1.10
Add validation of input config.json against spec.json.

## 0.1.9
Add configurable validation of schema for all records in BasicRead test: [#4345](https://github.com/airbytehq/airbyte/pull/4345)

The validation is ON by default. 
To disable validation for the source you need to set `validate_schema: off` in the config file.

## 0.1.8
Fix cursor_path to support nested and absolute paths: [#4552](https://github.com/airbytehq/airbyte/pull/4552)

## 0.1.7
Add: `test_spec` additionally checks if Dockerfile has `ENV AIRBYTE_ENTRYPOINT` defined and equal to space_joined `ENTRYPOINT`

## 0.1.6
Add test whether PKs present and not None if `source_defined_primary_key` defined: [#4140](https://github.com/airbytehq/airbyte/pull/4140)

## 0.1.5
Add configurable timeout for the acceptance tests: [#4296](https://github.com/airbytehq/airbyte/pull/4296)

