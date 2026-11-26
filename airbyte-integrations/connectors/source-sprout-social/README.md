# Sprout Social source

This is a declarative connector built with the [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview). For details on the underlying YAML format, see the [Low-Code CDK Overview](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

For user-facing documentation and setup guides, see the connector's page on [docs.airbyte.com](https://docs.airbyte.com/integrations/sources/sprout-social).

## Development

For local development and testing, see [Developing Connectors Locally](https://docs.airbyte.com/connector-development/local-connector-development).

### Editing metrics

Sprout Social needs an explicit metric list for each network type. The lists are in `definitions.metric_lists` in `manifest.yaml` (`post_metrics` and `profile_metrics`), keyed by Sprout's `network_type` (`facebook`, `fb_instagram_account`, `linkedin_company`, ...). A new metric also needs a property in that stream's schema. To support another network, give it a list in both maps.

### Unit tests

`unit_tests/` pins the partitioning, paging, date slicing, rate limiting and error handling against a mocked Sprout Social API:

```bash
cd unit_tests
poetry install
poetry run pytest
```
