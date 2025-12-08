import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Get started with direct connectors: Connector MCP

In this tutorial, you'll install and run Airbyte's connector MCP server locally, connect the MCP server to Claude Code or your preferred agent, and learn to use natural language to explore your Stripe data in your third-party service.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AIs. It assumes you have basic knowledge of the following.

- Claude Code or the agent of your choice
- AI agents
- MCP servers
- Stripe, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have installed the following software.

- Claude Code or the agent of your choice
- Python version XXX or later <!-- what is the minimum version of Python supported? -->
- A Python package manager like [uv](https://github.com/astral-sh/uv)

## Part 1: Clone the Connector MCP repository

<!-- Right now it's in the Sonar repo / connector-mcp folder. This is going to be broken out into its own public repo shortly, but for now this is how it works. -->

```bash
git clone https://github.com/airbytehq/sonar/
```

Once git finishes cloning, change directory into your repo.

```bash
cd sonar/connector-mcp
```

## Part 2: Configure the connector you want to use

### Create `configured_connectors.yaml`

The `configured_connectors.yaml` file defines which direct connectors you are making available through the MCP and which secrets you need to authentication.

1. Create a filed called `configured_connectors.yaml`. It's easiest to add this file to the root, but if you want to add it somewhere else, you can instruct the MCP where to find it later.

2. Add your connector definition to this file.

    ```yaml
    # Connector definitions
    connectors:
    - id: stripe
        type: local
        connector_name: stripe
        description: "My Stripe API connector"
        secrets:
            api_key: STRIPE_API_KEY
    ```

    <!-- Is it worth explaining the use of the path property instead of just the connector_name property? Can someone use this to run a local connector today? -->

    For a more complete example using multiple connectors, see [configured_connectors.yaml.example](https://github.com/airbytehq/sonar/blob/main/connector-mcp/configured_connectors.yaml.example). <!-- This link will change once the connector MCP is its own repo. It's not publicly accessible right now -->

### Define secrets in `.env`

1. Create a new file called `.env`.

2. Populate that file with your secret definitions. For example, if you defined a `api_key`/`STRIPE_API_KEY` key-value pair in `configured_connectors.yaml`, define `STRIPE_API_KEY` in your `.env` file.

    ```text
    STRIPE_API_KEY=your_stripe_api_key
    ```

## Part 3: Run the connector MCP

Use your package manager to run the Connector MCP.

- If your `configured_connectors.yaml` and `.env` files are in your repo root, run:

    ```bash
    uv run connector_mcp
    ```

- If your `configured_connectors.yaml` and `.env` files are in another location, specify that location with arguments.

    ```bash
    python -m connector_mcp path/to/configured_connectors.yaml path/to/.env
    ```

## Part 4: Use the MCP with your agent

<Tabs>
<TabItem value="Claude" label="Claude" default>

Open `claude.json` and add the following configuration.

```json
"mcpServers": {
    "connector-mcp": {
        "type": "stdio",
        "command": "uv",
        "args": [
            "--directory",
            "/path/to/connector-mcp",
            "run",
            "connector_mcp"
            ],
        "env": {}
    }
},
```

Alternatively, add the MCP through your command line tool.

```bash
claude mcp add --transport stdio connector-mcp -- \
  uv --directory /path/to/connector-mcp run connector_mcp
```

</TabItem>
</Tabs>

## Part 5: Work with your data

<!-- Instructions, tips, and sample queries to help people make the most of this connector. -->

## Summary

In this tutorial, you learned how to:

- Clone and set up Airbyte's Connector MCP
- Integrate the MCP with your AI agent
- Use natural language to interact with your data

## Next steps

- Continue adding new connectors to the MCP server by repeating Parts 2, 3, and 4 of this tutorial.
- If you need to run more complex processing and trigger effects based on your data, try the [Python](tutorial-python) tutorial to start using direct connectors with the Python SDK.
