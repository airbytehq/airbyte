# Height
This directory contains the manifest-only connector for `source-height`.

## Documentation reference:
Visit `https://height.notion.site/API-documentation-643aea5bf01742de9232e5971cb4afda` for API documentation

## Authentication setup
To set up the Height source connector, you'll need the Height API key that you could see once you login and navigate to `https://height.app/xxxxx/settings/api`, and copy your secret key
Website: `https://height.app`

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
This will create a dev image (`source-height:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-height build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-height test
```

