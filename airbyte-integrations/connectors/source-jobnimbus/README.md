# JobNimbus
This directory contains the manifest-only connector for `source-jobnimbus`.

The JobNimbus Airbyte connector enables seamless integration between JobNimbus, a popular CRM and project management tool, and your data pipeline. This connector allows you to automatically sync data from JobNimbus, including contacts records, task information, and more, into your preferred destination. It simplifies data extraction and helps you streamline workflows, enabling efficient analysis and reporting for enhanced business insights.

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
This will create a dev image (`source-jobnimbus:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-jobnimbus build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-jobnimbus test
```

