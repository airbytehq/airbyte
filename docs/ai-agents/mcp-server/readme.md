---
sidebar_position: 6
---

# Connector MCP server

Airbyte's Connector MCP server lets AI coding tools like Claude Code, Claude Desktop, Cursor, and Codex interact with your data sources through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Instead of writing code to fetch data, you configure a connector and register it with your AI tool. The AI tool then calls the connector's operations automatically based on your natural language prompts.

## What the MCP server does

The MCP server sits between your AI coding tool and Airbyte's [agent connectors](../connectors/). It exposes each connector's operations as MCP tools that AI assistants can discover and call. When you ask your AI tool a question like "show me the 10 most recent Gong calls," the tool calls the MCP server, which calls the connector, which calls the API.

The server handles:

- Discovering available entities and actions from the connector
- Executing operations and returning structured results
- Truncating large text fields to reduce token usage
- Field selection and exclusion to control what data is returned
- Downloading binary content like call recordings

## When to use the MCP server

The MCP server is the fastest way to give an AI coding tool access to your business data. It requires no application code. You configure a YAML file, register the server, and start prompting.

The following table compares the MCP server to the other ways you can use Airbyte's agent connectors.

| | MCP server | Python SDK | Hosted execution |
| --- | --- | --- | --- |
| **Best for** | AI coding tools (Claude Code, Cursor, Codex) | Custom agents and applications | Production multi-tenant apps |
| **Setup** | YAML config + one CLI command | Python project with code | Agent Engine account + API calls |
| **Code required** | None | Yes | Yes |
| **Credential storage** | Local `.env` file or Airbyte Cloud | Your application | Airbyte Cloud |
| **Search and filtering** | Supported (Cloud mode) | Depends on connector | Supported |

Choose the MCP server when you want to query data from an AI coding tool without writing application code. Choose the [Python SDK](../tutorials/quickstarts/tutorial-python) when you need programmatic control over connector operations in your own agent. Choose [hosted execution](../tutorials/quickstarts/tutorial-hosted) when you need centralized credential management for multiple end-users.

## How it works

The MCP server follows a single-connector-per-server architecture. Each server instance is configured with a YAML file that specifies which connector to use and how to authenticate. You can also use an aggregate configuration to run multiple connectors in a single server.

The server supports two execution modes:

- **Local mode**: The server installs a connector package (from PyPI, a git URL, or a local path) and calls the third-party API directly using your credentials.
- **Cloud mode**: The server calls the Airbyte Cloud API, which manages credentials and provides additional capabilities like indexed search.

A CLI called `adp` manages the full lifecycle:

1. **Discover** connectors with `adp connectors list-oss` or `adp connectors list-cloud`.
2. **Configure** a connector with `adp connectors configure`, which generates a YAML config file.
3. **Register** the server with your AI tool using `adp mcp add-to`.
4. **Use** the server by prompting your AI tool with natural language questions.

## Get started

Follow the [Connector MCP server tutorial](../tutorials/quickstarts/tutorial-mcp-server) to install the MCP server, configure a connector, and register it with your AI tool. You can be up and running in about 5 minutes.
