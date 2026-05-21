---
plan: all
sidebar_position: 2
---

import DocCardList from '@theme/DocCardList';
import SdkVsApi from '@site/static/\_ai-agents-sdk-vs-api.md';

# SDK

The Agent SDK (`airbyte_agent_sdk`) is the Python interface for Airbyte Agents. With one install you get typed connectors, automatic credential handling, direct execution, and patterns for exposing connectors as tools to AI agent frameworks.

This section walks through authenticate, add a connector, and execute operations. Deeper class and method signatures live in the [SDK reference](/ai-agents/reference/sdk).

## Choose your interface

<SdkVsApi />

## Log in and sign up

Log in or sign up at [app.airbyte.ai](https://app.airbyte.ai/).

## Install

Add the SDK to a [uv](https://docs.astral.sh/uv/)-managed project:

```bash
uv add airbyte-agent-sdk
```

To install into an existing virtual environment instead, run `uv pip install airbyte-agent-sdk`.

The install name uses dashes. The Python import name uses underscores: `from airbyte_agent_sdk import Workspace, connect`.

## End-to-end example

The example below authenticates with Airbyte and executes an operation against a GitHub connector. Before running this code, [add a GitHub connector](./add-connector) to your workspace through the [web app](../ui/add-connector) or the [REST API](../api/add-connector). The pages in this section explain each step in detail.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import connect

async def main():
    # Authenticate. The SDK reads AIRBYTE_CLIENT_ID and AIRBYTE_CLIENT_SECRET
    # from the environment.

    # Execute an operation against the connector. `connect()` resolves the
    # connector by its slug within the current workspace. No ID needed
    # when the workspace has one connector of this type.
    github = connect("github")
    try:
        # Parameter names are connector- and entity-specific. Call
        # `github.list_entities()` to see what each entity accepts.
        result = await github.execute("issues", "list", params={"per_page": 10})
        for row in result.data:
            print(row)
    finally:
        await github.close()

asyncio.run(main())
```

## Learn more

<DocCardList />
