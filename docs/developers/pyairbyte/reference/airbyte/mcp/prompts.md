---
sidebar_label: prompts
title: airbyte.mcp.prompts
---

MCP prompt definitions for the PyAirbyte MCP server.

This module defines prompts that can be invoked by MCP clients to perform
common workflows.

## annotations

## TYPE\_CHECKING

## Annotated

## Field

#### TEST\_MY\_TOOLS\_GUIDANCE

#### test\_my\_tools\_prompt

```python
def test_my_tools_prompt(
    scope: Annotated[
        str | None,
        Field(description=(
            "Optional free-form text to focus or constrain testing. "
            "This can be a single word, a sentence, or a paragraph "
            "describing the desired scope or constraints."), ),
    ] = None
) -> list[dict[str, str]]
```

Generate a prompt that instructs the agent to test available tools.

#### register\_prompts

```python
def register_prompts(app: FastMCP) -> None
```

Register all prompts with the FastMCP app.

