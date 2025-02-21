# Employment-Hero
This directory contains the manifest-only connector for [`source-employment-hero`](https://secure.employmenthero.com/).

## Documentation reference:
Visit `https://developer.employmenthero.com/api-references/#icon-book-open-introduction` for API documentation

## Authentication setup
`Employement Hero` uses Bearer token authentication, since code granted OAuth is not directly supported right now, Visit your developer profile for getting your OAuth keys. Refer `https://secure.employmenthero.com/app/v2/organisations/xxxxx/developer_portal/api` for more details.

## Getting your bearer token via postman

You can make a POST request from Postman to exchange your OAuth credentials for an `access token` to make requests.

First make an app to get the client ID and secret for authentication:

1. Go to developers portal Page:
- Visit `https://secure.employmenthero.com/app/v2/organisations/xxxxx/developer_portal/api`, select `Add Application` and input an app name. Select the `scopes` and set the redirect URI as `https://oauth.pstmn.io/v1/callback`.

2. Copy Your App Credentials:
 - After creating the app, you will see the Client ID and Client Secret.
 - Client ID: Copy this value as it will be your Client ID in Postman.
 - Client Secret: Copy this value as it will be your Client Secret in Postman.

3. Visit Postman via web or app and make a new request with following guidelines:
 - Open a new request - Goto Authorization tab - Select OAuth 2.0
 - Auth URL - `https://oauth.employmenthero.com/oauth2/authorize`
 - Access Token URL - `https://oauth.employmenthero.com/oauth2/token`
 - Set your client id and secret and leave scope and state as blank

Hit Get new Access token and approve via browser, Postman will collect a new `access_token` in the console response.

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
This will create a dev image (`source-employment-hero:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-employment-hero build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-employment-hero test
```

