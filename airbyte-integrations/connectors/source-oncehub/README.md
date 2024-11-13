# Oncehub
This directory contains the manifest-only connector for `source-oncehub`.

This is the Oncehub source that ingests data from the Oncehub API.

Oncehub is a no-code conversational journeys builder, integrating AI, chatbots, live chat, instant calls, and scheduled meetings https://oncehub.com/.

To use this source you must first create an account. Once logged in head over to Settings -&gt; API &amp; Webhooks and copy your API Key.
You can learn more about the API here https://developers.oncehub.com/reference/introduction

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
This will create a dev image (`source-oncehub:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-oncehub build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-oncehub test
```

