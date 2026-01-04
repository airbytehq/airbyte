# Interzoid
This directory contains the manifest-only connector for `source-interzoid`.

Interzoid is an AI-powered API platform providing data quality, data matching, and data enrichment capabilities that help Airbyte pipelines deliver higher data ROI. This connector enables you to call Interzoid’s APIs directly from your Airbyte workflows to match records, enrich attributes, normalize and standardize fields, or verify data as part of your extraction and loading processes. The result is cleaner, more consistent, and more actionable datasets flowing through your Airbyte integrations—without additional engineering overhead.

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
This will create a dev image (`source-interzoid:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-interzoid build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-interzoid test
```

