# Airbyte CI

This folder is a collection of systems, tools and scripts that are used to run Airbyte's CI/CD

The installation instructions for the `airbyte-ci` CLI tool cal be found here
[airbyte-ci/connectors/pipelines](connectors/pipelines/README.md)

## Tools

| Directory                                          | Description                                                                                                                   |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [`base_images`](connectors/base_images)            | A set of tools to build and publish Airbyte base connector images.                                                            |
| [`ci_credentials`](connectors/ci_credentials)      | A CLI tool to fetch connector secrets from GCP Secrets Manager.                                                               |
| [`connector_ops`](connectors/connector_ops)        | A python package with utils reused in internal packages.                                                                      |
| [`connectors_qa`](connectors/connectors_qa/)       | A tool to verify connectors have sounds assets and metadata.                                                                  |
| [`metadata_service`](connectors/metadata_service/) | Tools to generate connector metadata and registry.                                                                            |
| [`pipelines`](connectors/pipelines/)               | Airbyte CI pipelines, including formatting, linting, building, testing connectors, etc. Connector acceptance tests live here. |
| [`auto_merge`](connectors/auto_merge/)             | A tool to automatically merge connector pull requests.                                                                        |
