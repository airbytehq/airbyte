# Shiftbase Source

This is the repository for the Shiftbase source connector, built using the [manifest-only declarative framework](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview).
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/shiftbase).

## Streams

The Shiftbase connector supports the following data streams:

| Stream Name | Sync Mode | Description |
| :--- | :--- | :--- |
| `departments` | Full Refresh | Internal departments within the Shiftbase account. |
| `employees` | Full Refresh | List of employees. **Note:** The `name` field has been removed to minimize PII. |
| `absentees` | Full Refresh, Incremental | Records of employee absences and leave. |
| `employee_time_distribution` | Full Refresh, Incremental | Distribution of worked and planned hours per employee. |
| `availabilities` | Full Refresh, Incremental | Employee availability slots and preferences. |
| `shifts` | Full Refresh | Scheduled work shifts and roster details. |
| `users` | Full Refresh | User account details. **Note:** This stream is **flattened** and excludes all **PII** (names, emails, phones, addresses, etc.). |
| `employees_report` | Full Refresh | Employees report data. |
| `timesheet_detail_report` | Full Refresh, Incremental | Detailed timesheet report data. |
| `schedule_detail_report` | Full Refresh, Incremental | Detailed schedule report data. |

## Local development

### Prerequisites

This connector is manifest-only and does not require Python dependencies. The connector is defined entirely in `manifest.yaml`.

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:
```bash
airbyte-ci connectors --name=source-shiftbase build
```

An image will be available on your host with the tag `airbyte/source-shiftbase:dev`.

### Running as a docker container

Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-shiftbase:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-shiftbase:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-shiftbase:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-shiftbase:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=source-shiftbase test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure acceptance tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.

## Publishing a new version of the connector

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-shiftbase test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
    - bump the `dockerImageTag` value in `metadata.yaml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/sources/shiftbase.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.
