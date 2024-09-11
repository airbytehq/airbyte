# When_i_work
This directory contains the manifest-only connector for `source-when-i-work`.

## Documentation reference:
Visit `https://apidocs.wheniwork.com/external/index.html` for API documentation

## Authentication setup
`When I work` uses bearer token authentication,
Refer `https://apidocs.wheniwork.com/external/index.html?repo=login` for more details.

## Getting token via postman
Make a POST call to URL `https://api.login.wheniwork.com/login`
Along with body as raw-json with your login email and password
```bash
{
  "email": "xxxx@yyyy.com",
  "password": "123456789"
}
```
You will get a response containing token for your authentication.

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
This will create a dev image (`source-when-i-work:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-when-i-work build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-when-i-work test
```

