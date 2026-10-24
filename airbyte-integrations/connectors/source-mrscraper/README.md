# MrScraper
This directory contains the manifest-only connector for `source-mrscraper`.

Syncs the results MrScraper stores for your scraper runs: AI extraction runs and reruns, bulk jobs, manual and workflow runs, and Web Unblocker page fetches.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
For the repository's supported local-development tooling, see the [local connector development guide](../../../docs/platform/connector-development/local-connector-development.md).

### Unit tests
The unit tests mock the MrScraper API, so they need no credentials.
```bash
poe test-unit-tests
```

### Build
This will create a dev image (`airbyte/source-mrscraper:dev`) that you can use to test the connector locally.
```bash
airbyte-cdk image build
```

### Test
This will run the standard connector tests declared in `acceptance-test-config.yml`.
```bash
airbyte-cdk connector test
```

To read from a real account, put `{"api_key": "<your MrScraper API token>"}` in `secrets/config.json` (ignored by git) and run:
```bash
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-mrscraper:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```
