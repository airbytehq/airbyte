# airbyte-lib

airbyte-lib is a library that allows to run Airbyte syncs embedded into any Python application, without the need to run Airbyte server.

## Development

* Make sure [Poetry is installed](https://python-poetry.org/docs/#).
* Run `poetry install`
* For examples, check out the `examples` folder. They can be run via `poetry run python examples/<example file>`
* Unit tests and type checks can be run via `poetry run pytest`

## Validating source connectors

To validate a source connector for compliance, the `airbyte-lib-validate-source` script can be used. It can be used like this:

```
airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json
```

The script will install the python package in the provided directory, and run the connector against the provided config. The config should be a valid JSON file, with the same structure as the one that would be provided to the connector in Airbyte. The script will exit with a non-zero exit code if the connector fails to run.