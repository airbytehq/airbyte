# Pretix
This directory contains the manifest-only connector for `source-pretix`.

[Pretix](https://pretix.eu/about/en/) connector enables seamless data integration with the Pretix event ticketing platform, allowing users to sync ticket sales, attendee information, event data, and other metrics directly into their data warehouse or analytics tools. This connector supports automated data extraction for efficient, reporting and data-driven insights across events managed in Pretix.

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
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-pretix:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-pretix build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-pretix test
```

