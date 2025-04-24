# Uservoice
This directory contains the manifest-only connector for `source-uservoice`.

Airbyte connector for UserVoice.com allows users to efficiently extract data from the UserVoice  and integrate it with various data destinations. This connector can sync data such as user feedback, suggestions, comments, tickets, and support metrics, providing a streamlined way to analyze and act on customer feedback. It supports incremental data syncs, ensuring that new or updated data is captured without duplication. The connector is designed for easy setup, enabling seamless integration with UserVoice&#39;s API to ensure your customer insights are always up to date.

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
This will create a dev image (`source-uservoice:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-uservoice build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-uservoice test
```

