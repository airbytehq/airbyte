# Contributing to source-arxiv

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Connector type

`source-arxiv` is a manifest-only low-code source connector. Its behavior is defined in `manifest.yaml`; it does not use custom Python components.

## Local development

Run unit tests from the connector directory:

```bash
poetry -C unit_tests run pytest unit_tests -x
```

Run the low-code connector test suite:

```bash
airbyte-cdk connector test .
```

The arXiv API is public and does not require credentials. Test configs should include a small `search_query`, such as `cat:cs.AI`, and a small `page_size` to avoid unnecessary API traffic.

## API constraints

The arXiv API Terms of Use require no more than one request every three seconds and a single connection at a time. The connector uses a declarative HTTP API budget to throttle requests accordingly.
