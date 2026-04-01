# Linkrunner
This directory contains the manifest-only connector for `source-linkrunner`.

Linkrunner is a Mobile Measurement Partner (MMP) that helps track user journeys from first click to revenue generation. This connector extracts campaign data and attributed user analytics from Linkrunner&#39;s Data API, enabling comprehensive mobile attribution reporting and analysis. Supports filtering by campaign status, advertising channels (Google, Meta, TikTok), and time-based attribution data with automatic pagination and parent-child stream relationships.

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
This will create a dev image (`source-linkrunner:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-linkrunner build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-linkrunner test
```

