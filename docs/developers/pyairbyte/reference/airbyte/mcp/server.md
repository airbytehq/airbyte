---
sidebar_label: server
title: airbyte.mcp.server
---

Experimental MCP (Model Context Protocol) server for PyAirbyte connector management.

## asyncio

## sys

## FastMCP

## set\_mcp\_mode

## initialize\_secrets

## register\_cloud\_ops\_tools

## register\_connector\_registry\_tools

## register\_local\_ops\_tools

## register\_prompts

#### app

The Airbyte MCP Server application instance.

#### main

```python
def main() -> None
```

@private Main entry point for the MCP server.

This function starts the FastMCP server to handle MCP requests.

It should not be called directly; instead, consult the MCP client documentation
for instructions on how to connect to the server.

