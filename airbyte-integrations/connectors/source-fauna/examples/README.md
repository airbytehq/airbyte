This directory contains files for manual usage, and example files for setting up the Fauna Airbyte
Connector.

- `config_localhost.json`: A config file, which will connect to a local Fauna container, and read
  documents from it.
- `config_sample.json`: A sample config file. This demonstrates the format of the config, and
  shows an example of a completed configuration.
- `sample_state_full_sync.json`: A sample state file for picking up a partially failed full sync.
- `configured_catalog.json`: A configured Airbyte catalog, which will run a single full sync.
- `setup_database.fql`: Evaling this file with the fauna shell will setup the local database for
  testing. See below for instructions on running the connector locally.
- `secret_config.json`: This is the config that should be placed in `secrets/config.json`, and
  will produce the records at `integration_tests/expected_records.jsonl`. Note that if you run this
  yourself, you will need to manually setup the database, and the `ts` field will be incorrect.

# Running locally

These examples use the Fauna Shell, which can be downloaded here: https://github.com/fauna/fauna-shell

First, start a local fauna container:

```
docker run --rm --name faunadb -p 8443:8443 fauna/faunadb
```

In another terminal, cd into the connector directory:

```
cd airbyte-integrations/connectors/source-fauna
```

Once started the container is up, setup the database:

```
fauna eval "$(cat examples/setup_database.fql)" --domain localhost --port 8443 --scheme http --secret secret
```

Finally, run the connector:

```
python main.py spec
python main.py check --config examples/config_localhost.json
python main.py discover --config examples/config_localhost.json
python main.py read --config examples/config_localhost.json --catalog examples/configured_catalog.json
```
