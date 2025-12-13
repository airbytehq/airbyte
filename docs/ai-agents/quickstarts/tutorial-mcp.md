---
sidebar_label: "Connector MCP tutorial"
sidebar_position: 2
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent connector tutorial: Connector MCP

In this tutorial, you'll install and run Airbyte's connector MCP server locally, connect the MCP server to Claude Code or your preferred agent, and learn to use natural language to explore your data. This tutorial uses Stripe, but if you don't have a Stripe account, you can use one of Airbyte's other agent connectors.

:::warning
The Connector MCP server is experimental. It's quick and easy to set up, but it affords less control over how you use agent connectors compared to the Python SDK. Data goes directly from the API to your AI agent.

Feel free to try the MCP server, but it's better to use the [Python SDK](tutorial-python) to build a more robust agent.
:::

## Overview

This tutorial is for AI engineers and other technical users who work with data and AIs. It assumes you have basic knowledge of the following.

- Claude Code or the AI agent of your choice
- MCP servers
- Stripe, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have installed the following software.

- Claude Code or the agent of your choice, and the plan necessary to run it locally
- [Python](https://www.python.org/downloads/) version 3.13.7 or later
- [uv](https://github.com/astral-sh/uv)
- An account with Stripe, or a different third-party [supported by agent connectors](https://github.com/airbytehq/airbyte-agent-connectors/tree/main/connectors).

## Part 1: Clone the Connector MCP repository

Clone the Connector MCP repository.

```bash
git clone https://github.com/airbytehq/airbyte-agent-connectors
```

Once git finishes cloning, change directory into your repo.

```bash
cd airbyte-agent-connectors/airbyte-agent-mcp
```

## Part 2: Configure the connector you want to use

### Create a connector configuration file

The `configured_connectors.yaml` file defines which agent connectors you are making available through the MCP and which secrets you need for authentication.

1. Create a file called `configured_connectors.yaml`. It's easiest to add this file to the root, but if you want to add it somewhere else, you can instruct the MCP where to find it later.

2. Add your connector definition to this file. The `connector_name` field specifies which connector to load from the [Airbyte AI Connectors registry](https://connectors.airbyte.ai/registry.json). The keys under `secrets` are logical names that must match environment variables in your `.env` file.

    ```yaml title="configured_connectors.yaml"
    connectors:
      - id: stripe
        type: local
        connector_name: stripe
        description: "My Stripe API connector"
        secrets:
          api_key: STRIPE_API_KEY
    ```

### Define secrets in `.env`

1. Create a new file called `.env`.

2. Populate that file with your secret definitions. For example, if you defined a `api_key`/`STRIPE_API_KEY` key-value pair in `configured_connectors.yaml`, define `STRIPE_API_KEY` in your `.env` file.

    ```text title=".env"
    STRIPE_API_KEY=your_stripe_api_key
    ```

## Part 3: Run the Connector MCP

Use your package manager to run the Connector MCP.

1. If your `configured_connectors.yaml` and `.env` files are not in the repository root directory, specify their location with arguments before running the MCP.

    ```bash
    python -m connector_mcp path/to/configured_connectors.yaml path/to/.env
    ```

2. Run the MCP.

    ```bash
    uv run connector_mcp
    ```

## Part 4: Use the Connector MCP with your agent

<Tabs>
<TabItem value="Claude" label="Claude" default>

1. Add the MCP through your command line tool.

    ```bash
    claude mcp add --transport stdio connector-mcp -- \
    uv --directory /path/to/connector-mcp run connector_mcp
    ```

    Alternatively, open `.claude.json` and add the following configuration. Take extra care to get the path to the connector MCP correct. Claude expects the path from the root of your machine, not a relative path.

    ```json title=".claude.json"
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

2. Run Claude.

    ```bash
    claude
    ```

3. Verify the MCP server is running.

    ```bash
    /mcp
    ```

    You should see something like this.

    ```bash
    Connector-mcp MCP Server

    Status: ✔ connected
    Command: uv
    Args: --directory /path/to/connector-mcp run connector_mcp
    Config location: /path/to/.claude.json [project: /path/to/connector-mcp]
    Capabilities: tools
    Tools: 3 tools
    
    ❯ 1. View tools
      2. Reconnect
      3. Disable                   
    ```

4. Press <kbd>Esc</kbd> to go back to the main Claude prompt screen. You're now ready to work.

</TabItem>
<TabItem value="Other" label="Other">

Connector MCP runs as a standard MCP server over stdio. Any MCP-compatible client that supports custom stdio servers can use it by running the same command shown in the Claude tab. Refer to your client's documentation for how to add a custom MCP server.

The key configuration elements are:

- **Transport**: stdio
- **Command**: `uv`
- **Arguments**: `--directory /path/to/connector-mcp run connector_mcp`

</TabItem>
</Tabs>

## Part 5: Work with your data

Once your agent connects to the Connector MCP, you can use natural language to explore and interact with your data. The MCP server exposes three tools to your agent: one to list configured connectors, one to describe what a connector can do, and one to execute operations against your data sources.

### Verify your setup

Start by confirming your connector is properly configured. Ask your agent something like:

"List all configured connectors and tell me which entities and actions are available for the stripe connector."

Your agent discovers the available connectors and describes the Stripe connector's capabilities, showing you entities like `customers` and the actions you can perform on them, like `list` and `get`.

### Explore your data

Once you've verified your setup, you can start exploring your data with natural language queries. Here are some examples using Stripe:

<!-- vale off -->
- "List the 10 most recent Stripe customers and show me their email, name, and account balance."
- "Get the details for customer cus_ABC123 and show me all available fields."
- "How many customers do I have in Stripe? List them grouped by their creation month."
<!-- vale off -->

Your agent translates these requests into the appropriate API calls, fetches the data, and presents it in a readable format.

### Ask analytical questions

You can also ask your agent to analyze and summarize data across multiple records:

<!-- vale off -->
- "Find any Stripe customers who have a negative balance and list them with their balance amounts."
- "Summarize my Stripe customers by showing me the total count and the date range of when they were created."
<!-- vale off -->

The agent can combine multiple API calls and reason over the results to answer more complex questions.

### Tips for effective queries

When working with your data through the MCP, keep these tips in mind:

- Be specific about which connector you want to use if you have multiple configured (for example, "Using the stripe connector, list customers").
- Start with broad queries to understand what data is available, then drill down into specific records.
- If you're unsure what fields are available, ask your agent to describe the connector's entities first.
- For large datasets, specify limits in your queries to avoid overwhelming responses (for example, "Show me the first 20 customers").

## Summary

In this tutorial, you learned how to:

- Clone and set up Airbyte's Connector MCP
- Integrate the MCP with your AI agent
- Use natural language to interact with your data

## Next steps

- Continue adding new connectors to the MCP server by repeating Parts 2, 3, and 4 of this tutorial.

    You can configure multiple connectors in the same file. Here's an example:

    ```yaml title="configured_connectors.yaml"
    connectors:
    - id: stripe
        type: local
        connector_name: stripe
        description: "Stripe connector from Airbyte registry"
        secrets:
        api_key: STRIPE_API_KEY
    - id: github
        type: local
        connector_name: github
        description: "GitHub connector from Airbyte registry"
        secrets:
        token: GITHUB_TOKEN
    ```

- If you need to run more complex processing and trigger effects based on your data, try the [Python](tutorial-python) tutorial to start using agent connectors with the Python SDK.
