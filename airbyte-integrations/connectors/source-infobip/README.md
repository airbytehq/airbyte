# Infobip
This directory contains the manifest-only connector for `source-infobip`.

This is the Infobip source that ingests data from the infobip API.

Infobip drives deeper customer engagement with secure, personalized communications across SMS, RCS, Email, Voice, WhatsApp, and more https://www.infobip.com/

In order to use this source, you must first create an Infobip account. Once logged in, you can head over to Developer Tools in the sidebar and click on API Keys. Here you can generate a new API key for authenticating.

You can learn more about the API here https://www.infobip.com/docs/api

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
This will create a dev image (`source-infobip:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-infobip build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-infobip test
```

