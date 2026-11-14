# BambooHR connector

## API behavior

The [vendor specification](https://github.com/BambooHR/bhr-api-python/blob/main/specs/public.yaml)
defines no pagination parameters for these six endpoints:

- `POST /reports/custom`
- `GET /employees/directory` (returns only Active employees)
- `GET /meta/fields`
- `GET /time_off/requests`
- `GET /time_tracking/timesheet_entries`
- `GET /employees/{id}`

Paths are relative to the company's `v1/` API base.

## Incremental limitations

- The directory and field metadata endpoints expose no vendor cursor.
- Custom reports remain full refresh: `POST /reports/custom` is deprecated.
  Incremental support is deferred to the Datasets migration.
- Employees retain the compatibility placeholder cursor, not a last-changed cursor.
- Time-off `start`/`end` filters select requests whose date ranges overlap the
  window, not their `created` timestamps. The 365-day lookback reduces missed
  retroactive edits but cannot capture every historical change.
- Timesheet entries are limited to the last 365 days. Reads clamp their start to
  364 days ago and replay 30 days to pick up recent edits.

## Schema compatibility

`meta_fields_stream.id` remains a string even though the vendor specification
allows strings or integers: the 14-day production review found no record schema
validation errors for this field. Primary keys, existing date formats and types,
and cursor replacements are deferred to a breaking release.

## Tests

From `unit_tests/`, run `poetry install --no-root` and
`poetry run pytest mock_server/ -vv`. Mock reads do not require credentials.
Live acceptance tests require a valid company and API key with time-tracking access.
