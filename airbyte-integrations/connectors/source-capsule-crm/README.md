# Capsule CRM
This directory contains the manifest-only connector for `source-capsule-crm`.

Capsule CRM connector  enables seamless data syncing from Capsule CRM to various data warehouses, helping businesses centralize and analyze customer data efficiently. It supports real-time data extraction of contacts, opportunities, and custom fields, making it ideal for comprehensive CRM analytics and reporting.

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
This will create a dev image (`source-capsule-crm:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-capsule-crm build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-capsule-crm test
```

