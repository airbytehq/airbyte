# AgileCRM
This directory contains the manifest-only connector for `source-agilecrm`.

The [Agile CRM](https://agilecrm.com/) Airbyte Connector allows you to sync and transfer data seamlessly from Agile CRM into your preferred data warehouse or analytics tool. With this connector, you can automate data extraction for various Agile CRM entities, such as contacts, companies, deals, and tasks, enabling easy integration and analysis of your CRM data in real-time. Ideal for businesses looking to streamline data workflows and enhance data accessibility.

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
This will create a dev image (`source-agilecrm:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-agilecrm build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-agilecrm test
```

