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

## Employee resources and applicant tracking

Employee time-off policies, trainings, and goals read one endpoint per employee
returned by the directory. The directory contains only Active employees, so these
streams do not include records for employees missing from the directory. Policies
and trainings include `employeeId`; goals include `employee_id` because a shared
goal can appear under multiple employees.

Users, training types, training categories, and employee trainings return objects
keyed by ID. Employee trainings return `[]` when empty. Training categories inside
a training type can also be an empty array rather than an object.

Job applications follow `nextPageUrl` until `paginationComplete` is true or the
next URL is absent. The vendor fixes the page size. Applications remain full
refresh because `newSince` excludes updates to existing applications.

The API key owner needs training-settings access for training types, ATS settings
access for job openings and applications, and Benefits Administration permission
for dependents. Dependents contain masked personal identifiers and are not a
suggested stream.

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
