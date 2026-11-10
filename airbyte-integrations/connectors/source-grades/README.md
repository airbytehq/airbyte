# Grades.com source

This is a declarative (manifest-only) connector for [Grades.com](https://www.grades.com), the review management platform.
For details on the underlying YAML format, see the [Low-Code CDK Overview](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

For user-facing documentation and setup guides, see the connector's page on
[docs.airbyte.com](https://docs.airbyte.com/integrations/sources/grades).

## Development

For local development and testing, see [Developing Connectors Locally](https://docs.airbyte.com/connector-development/local-connector-development).
The acceptance tests read `secrets/config.json` (shape: `integration_tests/sample_config.json`): a Grades.com API key with
the scopes `reviews:read` and `companies:read`.
