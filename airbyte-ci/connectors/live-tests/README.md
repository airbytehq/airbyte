# Connector Live Testing

This project contains utilities for running connector tests against live data.

## Requirements

- `docker`
- `Python ^3.10`
- `pipx`
- `poetry`

## Install

```bash
# From airbyte-ci/connectors/live-tests
poetry install
```


## Regression tests

We created a regression test suite to run tests to compare the outputs of connector commands on different versions of the same connector.

## Validation tests

The validation test suite makes assertions about the output of airbyte commands for the target version of the connector only.

## Tutorial(s)

- [Loom Walkthrough (Airbyte Only)](https://www.loom.com/share/97c49d7818664b119cff6911a8a211a2?sid=4570a5b6-9c81-4db3-ba33-c74dc5845c3c)
- [Internal Docs (Airbyte Only)](https://docs.google.com/document/d/1pzTxJTsooc9iQDlALjvOWtnq6yRTvzVtbkJxY4R36_I/edit)

### How to Use

> ⚠️ **Note:** While you can use this tool without building a dev image, to achieve your goals you will likely need to have installed [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) and know how to build a dev image.

You can run the existing test suites with the following command:

#### With local connection objects (`config.json`, `catalog.json`, `state.json`)

```bash
poetry run pytest src/live_tests \
 --connector-image=airbyte/source-faker \
 --config-path=<path-to-config-path> \
 --catalog-path=<path-to-catalog-path> \
 --target-version=dev \
 --pr-url=<PR-URL> # The URL of the PR you are testing
```

#### Using a live connection

The live connection objects will be fetched.

```bash
 poetry run pytest src/live_tests \
 --connector-image=airbyte/source-faker \
 --target-version=dev \
  --pr-url=<PR-URL> # The URL of the PR you are testing
```

You can also pass local connection objects path to override the live connection objects with `--config-path`, `--state-path` or `--catalog-path`.

#### Test artifacts

The test suite run will produce test artifacts in the `/tmp/regression_tests_artifacts/` folder.
**They will get cleared after each test run on prompt exit. Please do not copy them elsewhere in your filesystem as they contain sensitive data that are not meant to be stored outside of your debugging session!**

##### Artifacts types

- `report.html`: A report of the test run.
- `stdout.log`: The collected standard output following the command execution
- `stderr.log`: The collected standard error following the command execution
- `http_dump.mitm`: An `mitmproxy` http stream log. Can be consumed with `mitmweb` (version `>=10`) for debugging.
- `http_dump.har`: An `mitmproxy` http stream log in HAR format (a JSON encoded version of the mitm dump).
- `airbyte_messages`: A directory containing `.jsonl` files for each message type (logs, records, traces, controls, states etc.) produced by the connector.
- `duck.db`: A DuckDB database containing the messages produced by the connector.
- `dagger.log`: The log of the Dagger session, useful for debugging errors unrelated to the tests.

**Tests can also write specific artifacts like diffs under a directory named after the test function.**

```
/tmp/regression_tests_artifacts
└── session_1710754231
    ├── duck.db
    |── report.html
    ├── command_execution_artifacts
    │   └── source-orb
    │       ├── check
    │       │   ├── dev
    │       │   │   ├── airbyte_messages
    │       │   │   │   ├── connection_status.jsonl
    │       │   │   │   └── logs.jsonl
    │       │   │   ├── http_dump.har
    │       │   │   ├── http_dump.mitm
    │       │   │   ├── stderr.log
    │       │   │   └── stdout.log
    │       │   └── latest
    │       │       ├── airbyte_messages
    │       │       │   ├── connection_status.jsonl
    │       │       │   └── logs.jsonl
    │       │       ├── http_dump.har
    │       │       ├── http_dump.mitm
    │       │       ├── stderr.log
    │       │       └── stdout.log
    │       ├── discover
    │       │   ├── dev
    │       │   │   ├── airbyte_messages
    │       │   │   │   └── catalog.jsonl
    │       │   │   ├── http_dump.har
    │       │   │   ├── http_dump.mitm
    │       │   │   ├── stderr.log
    │       │   │   └── stdout.log
    │       │   └── latest
    │       │       ├── airbyte_messages
    │       │       │   └── catalog.jsonl
    │       │       ├── http_dump.har
    │       │       ├── http_dump.mitm
    │       │       ├── stderr.log
    │       │       └── stdout.log
    │       ├── read-with-state
    │       │   ├── dev
    │       │   │   ├── airbyte_messages
    │       │   │   │   ├── logs.jsonl
    │       │   │   │   ├── records.jsonl
    │       │   │   │   ├── states.jsonl
    │       │   │   │   └── traces.jsonl
    │       │   │   ├── http_dump.har
    │       │   │   ├── http_dump.mitm
    │       │   │   ├── stderr.log
    │       │   │   └── stdout.log
    │       │   └── latest
    │       │       ├── airbyte_messages
    │       │       │   ├── logs.jsonl
    │       │       │   ├── records.jsonl
    │       │       │   ├── states.jsonl
    │       │       │   └── traces.jsonl
    │       │       ├── http_dump.har
    │       │       ├── http_dump.mitm
    │       │       ├── stderr.log
    │       │       └── stdout.log
    │       └── spec
    │           ├── dev
    │           │   ├── airbyte_messages
    │           │   │   └── spec.jsonl
    │           │   ├── stderr.log
    │           │   └── stdout.log
    │           └── latest
    │               ├── airbyte_messages
    │               │   └── spec.jsonl
    │               ├── stderr.log
    │               └── stdout.log
    └── dagger.log
```

#### HTTP Proxy and caching

We use a containerized `mitmproxy` to capture the HTTP traffic between the connector and the source. Connector command runs produce `http_dump.mitm` (can be consumed with `mitmproxy` (version `>=10`) for debugging) and `http_dump.har` (a JSON encoded version of the mitm dump) artifacts.
The traffic recorded on the control connector is passed to the target connector proxy to cache the responses for requests with the same URL. This is useful to avoid hitting the source API multiple times when running the same command on different versions of the connector.

### Custom CLI Arguments

| Argument                   | Description                                                                                                                                  | Required/Optional |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------| ----------------- |
| `--connector-image`        | Docker image name of the connector to debug (e.g., `airbyte/source-faker`, `airbyte/source-faker`).                                          | Required          |
| `--control-version`        | Version of the control connector for regression testing. Must be an unambiguous connector version (e.g. 1.2.3 rather than `latest`)          | Required          |
| `--target-version`         | Version of the connector being tested. (Defaults to dev)                                                                                     | Optional          |
| `--pr-url`                 | URL of the pull request being tested.                                                                                                        | Required          |
| `--connection-id`          | ID of the connection for live testing. If not provided, a prompt will appear to choose.                                                      | Optional          |
| `--config-path`            | Path to the custom source configuration file.                                                                                                | Optional          |
| `--catalog-path`           | Path to the custom configured catalog file.                                                                                                  | Optional          |
| `--state-path`             | Path to the custom state file.                                                                                                               | Optional          |
| `--http-cache`             | Use the HTTP cache for the connector.                                                                                                        | Optional          |
| `--run-id`                 | Unique identifier for the test run. If not provided, a timestamp will be used.                                                               | Optional          |
| `--auto-select-connection` | Automatically select a connection for testing.                                                                                               | Optional          |
| `--stream`                 | Name of the stream to test. Can be specified multiple times to test multiple streams.                                                        | Optional          |
| `--should-read-with-state` | Specify whether to read with state. If not provided, a prompt will appear to choose.                                                         | Optional          |
| `--disable-proxy`          | Specify whether to disable proxy. If not provided, a proxy will be enabled.                                                                  | Optional          |
| `--test-evaluation-mode`   | Whether to run tests in "diagnostic" mode or "strict" mode. In diagnostic mode, eligible tests will always pass unless there's an exception. | Optional          |
| `--connection-subset`      | The subset of connections to select from. Possible values are "sandboxes" or "all" (defaults to sandboxes).                                  | Optional          |

## Changelog

### 0.20.0
Support multiple connection objects in the regression tests suite.


### 0.19.10
Pin the connection retriever until we make required changes to support the new version.


### 0.19.8

Give ownership of copied connection object files to the image user to make sure it has permission to write them (config migration).

### 0.19.7

Mount connection objects to readable paths in the container for rootless images.

### 0.19.6

Write connector output to a different in container path to avoid permission issues now that connector images are rootless.

### 0.19.5

Fix `ZeroDivisionError` in Regression test tool

### 0.19.4

Update `connection_retriever` to 0.7.4

### 0.19.3

Update `get_container_from_id` with the correct new Dagger API.

### 0.19.2

Update Dagger to 0.13.3

### 0.19.1

Fixed the `UserDict` type annotation not found bug.

### 0.19.0

Delete the `debug`command.

### 0.18.8

Improve error message when failing to retrieve connection.
Ask to double-check that a sync ran with the control version on the selected connection.

### 0.18.7

Improve error message when failing to retrieve connection.

### 0.18.6

Disable the `SortQueryParams` MITM proxy addon to avoid double URL encoding.

### 0.18.5

Relax test_oneof_usage criteria for constant value definitions in connector SPEC output.

### 0.18.4

Bugfix: Use connection-retriever 0.7.2

### 0.18.3

Updated dependencies.

### 0.18.2

Allow live tests with or without state in CI.

### 0.18.1

Fix extra argument.

### 0.18.0

Add support for selecting from a subset of connections.

### 0.17.8

Fix the self-signed certificate path we bind to Python connectors.

### 0.17.7

Explicitly pass the control version to the connection retriever. Defaults to the latest released version of the connector under test.

### 0.17.6

Display diagnostic test with warning.

### 0.17.5

Performance improvements using caching.

### 0.17.4

Fix control image when running tests in CI.

### 0.17.3

Pin requests dependency.

### 0.17.2

Fix duckdb dependency.

### 0.17.1

Bump the connection-retriever version to fix deprecated query.

### 0.17.0

Enable running in GitHub actions.

### 0.16.0

Enable running with airbyte-ci.

### 0.15.0

Automatic retrieval of connection objects for regression tests. The connection id is not required anymore.

### 0.14.2

Fix KeyError when target & control streams differ.

### 0.14.1

Improve performance when reading records per stream.

### 0.14.0

Track usage via Segment.

### 0.13.0

Show test docstring in the test report.

### 0.12.0

Implement a test to compare schema inferred on both control and target version.

### 0.11.0

Create a global duckdb instance to store messages produced by the connector in target and control version.

### 0.10.0

Show record count per stream in report and list untested streams.

### 0.9.0

Make the regressions tests suite better at handling large connector outputs.

### 0.8.1

Improve diff output.

### 0.8.0

Regression tests: add an HTML report.

### 0.7.0

Improve the proxy workflow and caching logic + generate HAR files.

### 0.6.6

Exit pytest if connection can't be retrieved.

### 0.6.6

Cleanup debug files when prompt is closed.

### 0.6.5

Improve ConnectorRunner logging.

### 0.6.4

Add more data integrity checks to the regression tests suite.

### 0.6.3

Make catalog diffs more readable.

### 0.6.2

Clean up regression test artifacts on any exception.

### 0.6.1

Modify diff output for `discover` and `read` tests.

### 0.5.1

Handle connector command execution errors.

### 0.5.0

Add new tests and confirmation prompts.

### 0.4.0

Introduce DuckDB to store the messages produced by the connector.

### 0.3.0

Pass connection id to the regression tests suite.

### 0.2.0

Declare the regression tests suite.

### 0.1.0

Implement initial primitives and a `debug` command to run connector commands and persist the outputs to local storage.
