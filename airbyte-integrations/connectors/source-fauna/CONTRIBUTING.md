# source-fauna: Contributor notes

## Onboarding

If you already know how Airbyte works, read `bootstrap.md` for a quick introduction to this source.

If you are new to Airbyte, read `overview.md` for a longer explanation of what this connector does and how to use it.

## Running locally

Start a local Fauna container:

```bash
docker run --rm --name faunadb -p 8443:8443 fauna/faunadb
```

From the connector directory, set up the database:

```bash
cd airbyte-integrations/connectors/source-fauna
fauna eval "$(cat examples/setup_database.fql)" --domain localhost --port 8443 --scheme http --secret secret
```

Run the connector against the local database:

```bash
python main.py spec
python main.py check --config examples/config_localhost.json
python main.py discover --config examples/config_localhost.json
python main.py read --config examples/config_localhost.json --catalog examples/configured_catalog.json
```

To test recovery from partial failure, pass a state file. For example, induce a crash with bad data, update `examples/sample_state_full_sync.json` with the emitted state, then run:

```bash
python main.py read --config examples/config_localhost.json --catalog examples/configured_catalog.json --state examples/sample_state_full_sync.json
```

## Running integration tests

The integration tests require a secret config file.

1. Put the secret config in `secrets/config.json`. `examples/secret_config.json` shows the expected shape.
2. Build the connector:

   ```bash
   docker build . -t airbyte/source-fauna:dev
   ```

3. Run the integration tests:

   ```bash
   python -m pytest -p integration_tests.acceptance
   ```
