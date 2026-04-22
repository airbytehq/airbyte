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

## End-to-end example

The example below authenticates with Airbyte, adds a HubSpot connector for an end user, and executes an operation against it. The pages in this section explain each step in detail.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import Workspace, connect

async def main():
    # Authenticate. The SDK reads AIRBYTE_CLIENT_ID and AIRBYTE_CLIENT_SECRET
    # from the environment.
    async with Workspace() as ws:
        # Add a connector for the end user and store the returned ID.
        connector_id = await ws.create_connector(
            definition_id="<hubspot_definition_id>",
            name="My HubSpot Connector",
            credentials={
                "client_id": "<hubspot_client_id>",
                "client_secret": "<hubspot_client_secret>",
                "refresh_token": "<hubspot_refresh_token>",
            },
        )

    # Execute an operation against the connector.
    hubspot = connect("hubspot", connector_id=connector_id)
    result = await hubspot.execute("contacts", "list", params={"limit": 10})
    for row in result.data:
        print(row)

asyncio.run(main())
```

## Learn more

<DocCardList />
