# Interzoid Company Match API
This directory contains the manifest-only connector for `source-interzoid-company-match-api`.

This API provides a powerful mechanism for matching inconsistent company and organization name data within or across various data sources and datasets. It works by generating a similarity key using AI and specialized algorithms, so variations of the same organization name generate the same similarity key (GE, Gen Elec, GE Corp, etc.). Data can then be matched batched on similarity key rather than the organization name data itself for dramatically higher match rates.

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
This will create a dev image (`source-interzoid-company-match-api:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-interzoid-company-match-api build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-interzoid-company-match-api test
```

