# Google Calendar
[Google Calendar Connector](https://developers.google.com/calendar/api/v3/reference) source connector will syncs data between your Google Calendar and airbyte destination connector.
This directory contains the manifest-only connector for `source-google-calendar`.

Solves https://github.com/airbytehq/airbyte/issues/45995

# Create Credentials 
Follow the steps mentioned in the link [here](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id) and get the below required credentials to connect with your Google calendar connector

- Client ID
- Client secret
- Refresh token
- Calendar Id (Gmail address of the calendar you want to connect to)


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
This will create a dev image (`source-google-calendar:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-google-calendar build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-google-calendar test
```

