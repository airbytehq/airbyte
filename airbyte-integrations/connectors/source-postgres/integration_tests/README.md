This directory contains files used to run Connector Acceptance Tests.

- `abnormal_state.json` describes a connector state with a non-existing cursor value.
- `expected_records.txt` lists all the records expected as the output of the basic read operation.
- `incremental_configured_catalog.json` is a configured catalog used as an input of the `incremental` test.
- `seed.sql` is the query we manually ran on a test postgres instance to seed it with test data and enable CDC.
