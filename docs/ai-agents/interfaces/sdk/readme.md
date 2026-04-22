---
sidebar_position: 2
---

import DocCardList from '@theme/DocCardList';
import SdkVsApi from '@site/static/_ai-agents-sdk-vs-api.md';

# SDK

The Airbyte Agents Python SDK (`airbyte_agent_sdk`) is the Python front door to Airbyte Agents. With one install you get typed connectors, automatic credential handling, direct execution, natural-language queries across a workspace, and patterns for exposing connectors as tools to AI agent frameworks.

## Choose your interface

<SdkVsApi />

## Log in and sign up

Log in or sign up at [app.airbyte.ai](https://app.airbyte.ai/).

## Install

```bash
pip install airbyte-agent-sdk
```

The install name uses dashes. The Python import name uses underscores: `from airbyte_agent_sdk import Workspace, connect`.

## End-to-end example

The example below authenticates with Airbyte, adds a HubSpot connector, and executes an operation against it. The pages in this section explain each step in detail.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace, connect

async def main():
    # Authenticate. The SDK reads AIRBYTE_CLIENT_ID and AIRBYTE_CLIENT_SECRET
    # from the environment.
    async with Workspace() as ws:
        # Add a connector.
        await ws.create_connector(
            definition_id="<hubspot_definition_id>",
            name="My HubSpot Connector",
            credentials={
                "client_id": "<hubspot_client_id>",
                "client_secret": "<hubspot_client_secret>",
                "refresh_token": "<hubspot_refresh_token>",
            },
        )

        # Execute an operation against the connector. `connect()` resolves the
        # connector by its slug within the current workspace — no ID needed
        # when the workspace has one connector of this type.
        hubspot = connect("hubspot")
        try:
            # Parameter names are connector- and entity-specific. Call
            # `hubspot.list_entities()` to see what each entity accepts.
            result = await hubspot.execute("contacts", "list")
            for row in result.data:
                print(row)
        finally:
            await hubspot.close()

asyncio.run(main())
```

## Learn more

<DocCardList />
