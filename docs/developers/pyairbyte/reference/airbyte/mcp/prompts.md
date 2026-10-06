---
id: airbyte-mcp-prompts
title: "airbyte.mcp.prompts Module"
sidebar_label: "airbyte.mcp.prompts"
toc_max_heading_level: 5
---

# `airbyte.mcp.prompts` Module

MCP prompt definitions for the Airbyte Replication MCP server.

This module defines prompts that can be invoked by MCP clients to perform
common workflows.

# prompts module

MCP primitives registered by the `prompts` module of the `airbyte-mcp` server: **0** tool(s), **1** prompt(s), **0** resource(s).

## Prompts (1)

<a id="test-my-tools"></a>

### test-my-tools

Test all available MCP tools to confirm they are working properly

#### Arguments

| Name | Required | Description |
| --- | --- | --- |
| `scope` | no | Provide as a JSON string matching the following schema: \{"anyOf":[\{"type":"string"\},\{"type":"null"\}],"description":"Optional free-form text to focus or constrain testing. This can be a single word, a sentence, or a paragraph describing the desired scope or constraints."\} |