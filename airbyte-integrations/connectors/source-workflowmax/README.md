# Workflowmax
This directory contains the manifest-only connector for [`source-workflowmax`](https://app.workflowmax2.com/).

## Documentation reference:
Visit `https://app.swaggerhub.com/apis-docs/WorkflowMax-BlueRock/WorkflowMax-BlueRock-OpenAPI3/0.1#/` for V1 API documentation

## Authentication setup
`Workflowmax` uses bearer token authentication, You have to input your bearer access_token in the field of API key for authentication.

### Using postman to get access token 
- Move to Authorization tab of an empty http request and selected Oauth 2.0
- Set use token type as `access token`
- Set header prefix as `Bearer`
- Set grant type as `Authorization code`
- Check `Authorize using browser`
- Set Auth URL as `https://oauth.workflowmax2.com/oauth/authorize`
- Set Access token URL as `https://oauth.workflowmax2.com/oauth/token`
- Set Client ID, Client secret, Scope defined as your Workflowmax settings, Example Scope: `openid profile email workflowmax offline_access`
- Set state as any number, Example: `1`
- Set Client Authentication as `Send as Basic Auth Header`
  Click `Get New Access Token` for retrieving access token

Then authorize your source with the required information. 
1. Go to set up `The Source` page.
2. Enter your Workflowmax application's access token.
3. Click Save button.

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
This will create a dev image (`source-workflowmax:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-workflowmax build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-workflowmax test
```

