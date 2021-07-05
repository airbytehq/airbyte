# Changelog

## 0.1.8
Fix cursor_path to support nested and absolute paths: https://github.com/airbytehq/airbyte/pull/4552

## 0.1.7
Add: `test_spec` additionally checks if Dockerfile has `ENV AIRBYTE_ENTRYPOINT` defined and equal to space_joined `ENTRYPOINT`

## 0.1.6
Add test whether PKs present and not None if `source_defined_primary_key` defined: https://github.com/airbytehq/airbyte/pull/4140

## 0.1.5
Add configurable timeout for the acceptance tests: https://github.com/airbytehq/airbyte/pull/4296
