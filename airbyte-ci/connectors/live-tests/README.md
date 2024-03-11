# Connector Live Testing

This project contains utilities for running connector tests against live data.

## Requirements
* `docker`
* `Python ^3.10`
* `pipx`
* `poetry`

## Install
```bash
# From airbyte-ci/connectors/live-tests
pipx install .
# To install in editable mode for development
pipx install . --force --editable
```

## Commands

### `debug`

```
Usage: live-tests debug [OPTIONS] {check|discover|read|read-with-state|spec}

  Run a specific command on one or multiple connectors and persists the
  outputs to local storage.

Options:
  --connection-id TEXT
  --config-path FILE
  --catalog-path FILE
  --state-path FILE
  -c, --connector-image TEXT      Docker image name of the connector to debug
                                  (e.g. `airbyte/source-faker:latest`,
                                  `airbyte/source-faker:dev`)  [required]
  -o, --output-directory DIRECTORY
                                  Directory in which connector output and test
                                  results should be stored. Defaults to the
                                  current directory.
  -hc, --http-cache               Use the HTTP cache for the connector.
  --help                          Show this message and exit.
```

This command is made to run any of the following connector commands against one or multiple connector images.

**Available connector commands:**
* `spec`
* `check`
* `discover`
* `read` or `read_with_state` (requires a `--state-path` to be passed)

It will write artifacts to an output directory:
* `stdout.log`: The collected standard output following the command execution
* `stderr.log`: The collected standard error following the c
* `http_dump.txt`: An `mitmproxy` http stream log. Can be consumed with `mitmweb` (version `9.0.1`) for debugging.
* `airbyte_messages.db`: A DuckDB database containing the messages produced by the connector.
* `airbyte_messages`: A directory containing `.jsonl` files for each message type (logs, records, traces, controls, states etc.) produced by the connector.

#### Example
Let's run `debug` to check the output of `read` on two different versions of the same connector:

```bash
live-tests debug read \
--connector-image=airbyte/source-pokeapi:dev \
--connector-image=airbyte/source-pokeapi:latest \
--config-path=poke_config.json \
--catalog-path=configured_catalog.json
```

It will store the results in a `live_test_debug_reports` directory under the current working directory: 

```
live_tests_debug_reports
└── 1709547771
    └── source-pokeapi
        └── read
            ├── dev
            │   ├── airbyte_messages
            |   │   ├── duck.db # DuckDB database
            │   │   ├── logs.jsonl
            │   │   ├── records.jsonl
            │   │   └── traces.jsonl
            │   ├── http_dump.mitm # Consume it with mitmweb --rfile http_dump.mitm
            │   ├── stderr.log
            │   └── stdout.log
            └── latest
                ├── airbyte_messages
                │   ├── duck.db # DuckDB database
                │   ├── logs.jsonl
                │   ├── records.jsonl
                │   └── traces.jsonl
                ├── http_dump.mitm # Consume it with mitmweb --rfile http_dump.mitm
                ├── stderr.log
                └── stdout.log

```

You can also run the `debug` command on a live connection by passing the `--connection-id` option:

```bash
live-tests debug read \
--connector-image=airbyte/source-pokeapi:dev \
--connector-image=airbyte/source-pokeapi:latest \
--connection-id=<CONNECTION-ID>
```

##### Consuming `http_dump.mitm`
You can install [`mitmproxy`](https://mitmproxy.org/):
```bash
pipx install mitmproxy
```

And run:
```bash
mitmweb --rfile=http_dump.mitm
```

## Regression tests
We created a regression test suite to run tests to compare the outputs of connector commands on different versions of the same connector. 

You can run the existing test suites with the following command:

#### With local connection objects (`config.json`, `catalog.json`, `state.json`)
```bash
poetry run pytest src/live_tests/regression_tests \ 
--connector-image=airbyte/source-faker \
 --config-path=<path-to-config-path> \
 --catalog-path=<path-to-catalog-path> \
 --target-version=dev \
 --control-version=latest
```

#### Using a live connection
The live connection objects will be fetched.

```bash
 poetry run pytest src/live_tests/regression_tests \
 --connector-image=airbyte/source-faker \
 --connection-id=<CONNECTION-ID> \
 --target-version=dev \
 --control-version=latest 
 ```

You can also pass local connection objects path to override the live connection objects with `--config-path`, `--state-path` or `--catalog-path`.


## Changelog

### 0.4.0
Introduce DuckDB to store the messages produced by the connector.

### 0.3.0
Pass connection id to the regression tests suite.

### 0.2.0
Declare the regression tests suite.

### 0.1.0
Implement initial primitives and a `debug` command to run connector commands and persist the outputs to local storage.
