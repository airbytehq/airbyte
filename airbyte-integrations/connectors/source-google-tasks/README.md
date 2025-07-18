# Google Tasks
This directory contains the manifest-only connector for `source-google-tasks`.

## Documentation reference:
Visit `https://developers.google.com/tasks/reference/rest` for API documentation

## Authentication setup
`Source-productive` uses bearer token authentication,
Visit `https://support.google.com/googleapi/answer/6158849?hl=en&amp;ref_topic=7013279` for getting bearer token via OAuth2.0

## Setting postman for getting bearer token
Currently Code granted OAuth 2.0 is not directly supported by airbyte, thus you could setup postman for getting the bearer token which could be used as `api_key`,
Steps:
- Visit google cloud `https://console.cloud.google.com/apis/api/tasks.googleapis.com/metrics` and enable the tasks api service
- Go to the consent screen `https://console.cloud.google.com/apis/credentials/consent` and add your email for enabling postman testing access
- Visit `https://console.cloud.google.com/apis/credentials` and create new credentails for OAuth 2.0 and copy client id and client secret 
- Add callback url `https://oauth.pstmn.io/v1/callback` while credential creation
- Goto postman client and select new tab for setting authorization to OAuth 2.0
  - Set scope as `https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/tasks.readonly`
  - Set access token URL as `https://accounts.google.com/o/oauth2/token`
  - Set auth URL as `https://accounts.google.com/o/oauth2/v2/auth`
  - Click `Get New Access Token` and authorize via your google account
  - Copy the resulted bearer token and use it as credential for the connector

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
This will create a dev image (`source-google-tasks:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-google-tasks build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-google-tasks test
```

