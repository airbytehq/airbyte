# airbyte-lib

airbyte-lib is a library that allows to run Airbyte syncs embedded into any Python application, without the need to run Airbyte server.

## Development

* Make sure [Poetry is installed](https://python-poetry.org/docs/#).
* Run `poetry install`
* For examples, check out the `examples` folder. They can be run via `poetry run python examples/<example file>`
* Unit tests and type checks can be run via `poetry run pytest`

## Documentation

Regular documentation lives in the `/docs` folder. Based on the doc strings of public methods, we generate API documentation using [pdoc](https://pdoc.dev). To generate the documentation, run `poetry run generate-docs`. The documentation will be generated in the `docs/generate` folder. This needs to be done manually when changing the public interface of the library.

A unit test validates the documentation is up to date. 

## Validating source connectors

To validate a source connector for compliance, the `airbyte-lib-validate-source` script can be used. It can be used like this:

```
airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json
```

The script will install the python package in the provided directory, and run the connector against the provided config. The config should be a valid JSON file, with the same structure as the one that would be provided to the connector in Airbyte. The script will exit with a non-zero exit code if the connector fails to run.

For a more lightweight check, the `--validate-install-only` flag can be used. This will only check that the connector can be installed and returns a spec, no sample config required.