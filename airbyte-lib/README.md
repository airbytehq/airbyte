# airbyte-lib

airbyte-lib is a library that allows to run Airbyte syncs embedded into any Python application, without the need to run Airbyte server.

## Development

- Make sure [Poetry is installed](https://python-poetry.org/docs/#).
- Run `poetry install`
- For examples, check out the `examples` folder. They can be run via `poetry run python examples/<example file>`
- Unit tests and type checks can be run via `poetry run pytest`

## Release

- In your PR:
  - Bump the version in `pyproject.toml`
  - Add a changelog entry to the table below
- Once the PR is merged, go to Github and trigger the `Publish AirbyteLib Manually` workflow. This will publish the new version to PyPI.

## Secrets Management

AirbyteLib can auto-import secrets from the following sources:

1. Environment variables.
2. Variables defined in a local `.env` ("Dotenv") file.
3. [Google Colab secrets](https://medium.com/@parthdasawant/how-to-use-secrets-in-google-colab-450c38e3ec75).
4. Manual entry via [`getpass`](https://docs.python.org/3.9/library/getpass.html).

_Note: Additional secret store options may be supported in the future. [More info here.](https://github.com/airbytehq/airbyte-lib-private-beta/discussions/5)_

### Retrieving Secrets

```python
from airbyte_lib import get_secret, SecretSource

source = get_connection("source-github")
source.set_config(
   "credentials": {
      "personal_access_token": get_secret("GITHUB_PERSONAL_ACCESS_TOKEN"),
   }
)
```

The `get_secret()` function accepts an optional `source` argument of enum type `SecretSource`. If omitted or set to `SecretSource.ANY`, AirbyteLib will search all available secrets sources. If `source` is set to a specific source, then only that source will be checked. If a list of `SecretSource` entries is passed, then the sources will be checked using the provided ordering.

By default, AirbyteLib will prompt the user for any requested secrets that are not provided via other secret managers. You can disable this prompt by passing `prompt=False` to `get_secret()`.

### Versioning

Versioning follows [Semantic Versioning](https://semver.org/). For new features, bump the minor version. For bug fixes, bump the patch version. For pre-releases, append `dev.N` to the version. For example, `0.1.0dev.1` is the first pre-release of the `0.1.0` version.

## Documentation

Regular documentation lives in the `/docs` folder. Based on the doc strings of public methods, we generate API documentation using [pdoc](https://pdoc.dev). To generate the documentation, run `poetry run generate-docs`. The documentation will be generated in the `docs/generate` folder. This needs to be done manually when changing the public interface of the library.

A unit test validates the documentation is up to date.

## Connector compatibility

To make a connector compatible with airbyte-lib, the following requirements must be met:
* The connector must be a Python package, with a `pyproject.toml` or a `setup.py` file.
* In the package, there must be a `run.py` file that contains a `run` method. This method should read arguments from the command line, and run the connector with them, outputting messages to stdout.
* The `pyproject.toml` or `setup.py` file must specify a command line entry point for the `run` method called `source-<connector name>`. This is usually done by adding a `console_scripts` section to the `pyproject.toml` file, or a `entry_points` section to the `setup.py` file. For example:

```toml
[tool.poetry.scripts]
source-my-connector = "my_connector.run:run"
```

```python
setup(
    ...
    entry_points={
        'console_scripts': [
            'source-my-connector = my_connector.run:run',
        ],
    },
    ...
)
```

To publish a connector to PyPI, specify the `pypi` section in the `metadata.yaml` file. For example:

```yaml
data:
 # ...
 remoteRegistries:
   pypi:
     enabled: true
     packageName: "airbyte-source-my-connector"
```

## Validating source connectors

To validate a source connector for compliance, the `airbyte-lib-validate-source` script can be used. It can be used like this:

```bash
airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json
```

The script will install the python package in the provided directory, and run the connector against the provided config. The config should be a valid JSON file, with the same structure as the one that would be provided to the connector in Airbyte. The script will exit with a non-zero exit code if the connector fails to run.

For a more lightweight check, the `--validate-install-only` flag can be used. This will only check that the connector can be installed and returns a spec, no sample config required.

## Changelog

| Version     | PR                                                         | Description                                                                                                       |
| ----------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 0.1.0  | [#35184](https://github.com/airbytehq/airbyte/pull/35184) | Beta Release 0.1.0 |
| 0.1.0dev.2   | [#34111](https://github.com/airbytehq/airbyte/pull/34111)  | Initial publish - add publish workflow                                                                            |
