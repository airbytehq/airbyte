# FXMacroData

This directory contains the manifest-only `source-fxmacrodata` connector. It
reads macroeconomic announcements, release calendars, indicator catalogues and
FX reference rates from the [FXMacroData API](https://fxmacrodata.com/documentation/reference?utm_source=github&utm_medium=referral&utm_campaign=airbyte&utm_content=readme).

See the [connector documentation](../../../docs/integrations/sources/fxmacrodata.md)
for configuration fields, streams and access notes.

## Local development

USD data can be read without an API key, so `integration_tests/sample_config.json`
works as is. For other currencies or the `forex` stream, put a config with an
`api_key` at `secrets/config.json`.

Build the connector image from this directory:

```bash
airbyte-cdk image build
```

Then run connector commands through the image:

```bash
docker run --rm airbyte/source-fxmacrodata:dev spec

docker run --rm \
  --volume "$PWD/integration_tests:/config:ro" \
  airbyte/source-fxmacrodata:dev \
  check --config /config/sample_config.json
```

Run the standard connector tests and the mock-server unit tests:

```bash
airbyte-cdk connector test

cd unit_tests
poetry install
poetry run pytest .
```
