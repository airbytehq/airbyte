# OpenAI
This directory contains the manifest-only connector for `source-openai`.

OpenAI organization and ChatGPT Enterprise compliance source. Syncs organization members and pending invites from the OpenAI Admin API, daily completion usage aggregated by project, user, and model, and ChatGPT workspace user rosters (current and historical). For Enterprise workspaces, also syncs compliance conversation log metadata and message-level events from JSONL export files. Requires an OpenAI organization API key with admin access, a ChatGPT compliance API token, and a workspace ID. Supports incremental sync on usage and compliance log streams using a configurable start and end date (YYYY-MM-DD).

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
This will create a dev image (`source-openai:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-openai build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-openai test
```

