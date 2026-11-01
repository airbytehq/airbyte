# SAP HANA source

This is the repository for the SAP HANA source connector, written in Python on the Airbyte Python CDK and SAP's native
`hdbcli` driver. For information about how to use this connector within Airbyte, see
[the documentation](https://docs.airbyte.com/integrations/sources/sap-hana).

## Local development

### Prerequisites

- Python (`^3.11`)
- Poetry (`^2.0`) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

### Create credentials

Copy `integration_tests/sample_config.json` to `secrets/config.json` and fill in your SAP HANA connection details.
See `source_sap_hana/spec.json` for all options. `secrets` is git-ignored.

### Locally running the connector

```bash
poetry run source-sap-hana spec
poetry run source-sap-hana check --config secrets/config.json
poetry run source-sap-hana discover --config secrets/config.json
poetry run source-sap-hana read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Running tests

Unit tests, including the Airbyte CDK standard tests, run against an in-process fake SAP HANA backed by SQLite.
The connector's real SQL (`SYS.TABLES`, quoted identifiers, `NULLS FIRST`, `LIMIT`, `?` parameters) runs unchanged,
and the fake can inject real `hdbcli` connection errors (`-10807 Connection down`) to exercise reconnect and resume.
No HANA server is needed:

```bash
poetry run pytest unit_tests
```

Integration tests against a real SAP HANA (`secrets/config.json`) check schema conformance of every stream,
reconcile keyset pagination with `COUNT(*)`, and test the SSH tunnel through a throwaway Docker bastion:

```bash
poetry run pytest integration_tests -m integration -s
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run `airbyte-ci connectors --name=source-sap-hana build`

This builds `airbyte/source-sap-hana:dev` on top of the base image declared in `metadata.yaml`.

### Running as a docker container

```bash
docker run --rm airbyte/source-sap-hana:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-sap-hana:dev check --config /secrets/config.json
```

### Running our CI test suite

```bash
airbyte-ci connectors --name=source-sap-hana test
```

### Dependency Management

All dependencies are managed with Poetry. Add a runtime dependency with `poetry add <package-name>`, or a test
dependency with `poetry add --group dev <package-name>`.

### Publishing a new version of the connector

1. Make your changes and run the tests.
2. Bump the version: `dockerImageTag` in `metadata.yaml` and `version` in `pyproject.toml`.
3. Add an entry to the changelog in `docs/integrations/sources/sap-hana.md`.
4. Open a pull request.
