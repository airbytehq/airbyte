# Ayrshare source

This is a declarative connector built with the [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview). For details on the underlying YAML format, see the [Low-Code CDK Overview](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

For user-facing documentation and setup guides, see the connector's page on [docs.airbyte.com](https://docs.airbyte.com/integrations/sources/ayrshare).

## Development

For local development and testing, see [Developing Connectors Locally](https://docs.airbyte.com/connector-development/local-connector-development).

### Unit tests

`unit_tests/` pins the error handling, partitioning and paging against mocked Ayrshare responses (the profile streams need real Profile Keys to read live):

```bash
cd unit_tests
poetry install
poetry run pytest
```
