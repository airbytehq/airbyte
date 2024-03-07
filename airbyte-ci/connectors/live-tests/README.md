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
Usage: live-tests debug [OPTIONS] COMMAND

  Run a specific command on one or multiple connectors and persists the
  outputs to local storage.

Options:
  -c, --connector-image TEXT      Docker image name of the connector to debug
                                  (e.g. `source-faker:latest`, `source-
                                  faker:dev`)  [required]
  -o, --output-directory DIRECTORY
                                  Directory in which connector output and test
                                  results should be stored.
                                  Defaults to the current directory.
  --config-path FILE              Path to the connector config.
  --catalog-path FILE             Path to the connector catalog.
  --state-path FILE               Path to the connector state.
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
            │   │   ├── logs.jsonl
            │   │   ├── pokemon_records.jsonl
            │   │   └── traces.jsonl
            │   ├── http_dump.mitm
            │   ├── stderr.log
            │   └── stdout.log
            └── latest
                ├── airbyte_messages
                │   ├── logs.jsonl
                │   ├── pokemon_records.jsonl
                │   └── traces.jsonl
                ├── http_dump.mitm
                ├── stderr.log
                └── stdout.log

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

## Changelog

### 0.1.0
Implement initial primitives and a `debug` command to run connector commands and persist the outputs to local storage.
