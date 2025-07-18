# Microsoft Entra Id
This directory contains the manifest-only connector for `source-microsoft-entra-id`.

The Microsoft Entra ID Connector for Airbyte allows seamless integration with Microsoft Entra ID, enabling secure and automated data synchronization of identity and access management information. With this connector, users can efficiently retrieve and manage user, group, and directory data to streamline identity workflows and ensure up-to-date access control within their applications.

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
This will create a dev image (`source-microsoft-entra-id:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-microsoft-entra-id build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-microsoft-entra-id test
```

