---
sidebar_position: 6
---

# Agent Engine MCP server

Airbyte's Agent Engine MCP server lets AI agents interact with your data sources through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Instead of writing code to fetch data, you configure a connector and register it with your agent. The agent then calls the connector's operations automatically based on your natural language prompts.

## What the MCP server does

The MCP server sits between your agent and Airbyte's [agent connectors](../connectors/). It exposes each connector's operations as MCP tools that AI assistants can discover and call. When you prompt your agent, like `show me the 10 most recent Gong calls`, the agent calls the MCP server, which calls the connector, which calls the API.

The server handles:

- Discovering available entities and actions from the connector

- Executing operations and returning structured results

- Truncating large text fields to reduce token usage

- Field selection and exclusion to control what data the API returns

- Downloading binary content like call recordings

## When to use the MCP server

The MCP server is the fastest way to give an AI coding tool access to your data. It requires no code. You configure a YAML file, register the server, and start prompting.

## How it works

You configure each server instance with a YAML file that specifies which connector to use and how to authenticate. You can run a single connector per server, or use an [aggregate configuration](configuration#use-multiple-connectors-with-one-mcp-server) to run multiple connectors in one server.

The server supports two execution modes:

- **Open source mode**: The server installs a connector package (from PyPI, a git URL, or a local path) and calls the third-party API directly using your credentials.

- **Hosted mode**: The server calls the Airbyte Cloud API, which manages credentials and provides additional capabilities like indexed search through the [context store](../platform/context-store).

A command line tool called `agent-engine` manages the full lifecycle:

1. **Discover** connectors with `agent-engine connectors list-oss` or `agent-engine connectors list-cloud`.

2. **Configure** a connector with `agent-engine connectors configure`, which generates a YAML config file.

3. **Register** the server with your AI tool using `agent-engine mcp add-to`.

4. **Use** the server by prompting your AI tool with natural language questions.

## Get started

Follow the [Agent Engine MCP server tutorial](../tutorials/quickstarts/tutorial-mcp-server) to install the MCP server, configure a connector, and register it with your AI tool. You can be up and running in about 5 minutes.
