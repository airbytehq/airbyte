# NoCRM
This directory contains the manifest-only connector for `source-nocrm`.

[NoCRM](https://nocrm.io) connector enables seamless data integration between NoCRM.io, a lead management tool, and other platforms or data warehouses. It allows for the automated extraction and synchronization of lead data, activities, and contact details from NoCRM.io into analytics  systems, supporting data-driven decisions and streamlined workflows. 

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
This will create a dev image (`source-nocrm:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-nocrm build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-nocrm test
```

