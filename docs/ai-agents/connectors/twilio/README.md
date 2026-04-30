# Twilio

The Twilio agent connector is a Python package that equips AI agents to interact with Twilio through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Twilio REST API. Provides read and write access to core Twilio resources including accounts, calls, messages, recordings, conferences, incoming phone numbers, usage records, addresses, queues, transcriptions, and outgoing caller IDs. Write operations include sending SMS/MMS messages, placing outbound calls, and provisioning phone numbers. Uses HTTP Basic authentication with Account SID and Auth Token.


## Example questions

The Twilio connector is optimized to handle prompts like these.

- List all calls from the last 7 days
- Show me recent inbound SMS messages
- List all active phone numbers on my account
- Show me details for a specific call
- List all recordings
- Show me conference calls
- List usage records for my account
- Show me all queues
- List outgoing caller IDs
- Show me addresses on my account
- List transcriptions
- Send an SMS message to +15558675310 saying 'Hello from Twilio!'
- Place an outbound call to +15558675310 with the message 'Your appointment is confirmed'
- Provision a new phone number with area code 415
- Send a WhatsApp message to +15558675310
- Send an MMS with an image to +15558675310
- What are my top 10 most expensive calls this month?
- How many SMS messages did I send vs receive in the last 30 days?
- Summarize my usage costs by category
- Which phone numbers have the most incoming calls?
- Show me all failed messages and their error codes
- What is the average call duration for outbound calls?

## Unsupported questions

The Twilio connector isn't currently able to handle prompts like these.

- Delete a recording
- Delete a phone number
- Delete a message
- Create a new queue

## Installation

```bash
uv pip install airbyte-agent-sdk
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

@agent.tool_plain
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

@tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

mcp = FastMCP("Twilio Agent")

@mcp.tool()
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

The `connect()` factory returns a fully typed `TwilioConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

@agent.tool_plain
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

@tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

mcp = FastMCP("Twilio Agent")

@mcp.tool()
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
import json

from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

**FastMCP**

```python title="FastMCP"
import json

from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Twilio Agent")

@mcp.tool()
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Create](./REFERENCE.md#calls-create), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Messages | [List](./REFERENCE.md#messages-list), [Create](./REFERENCE.md#messages-create), [Get](./REFERENCE.md#messages-get), [Context Store Search](./REFERENCE.md#messages-context-store-search) |
| Incoming Phone Numbers | [List](./REFERENCE.md#incoming-phone-numbers-list), [Create](./REFERENCE.md#incoming-phone-numbers-create), [Get](./REFERENCE.md#incoming-phone-numbers-get), [Context Store Search](./REFERENCE.md#incoming-phone-numbers-context-store-search) |
| Recordings | [List](./REFERENCE.md#recordings-list), [Get](./REFERENCE.md#recordings-get), [Context Store Search](./REFERENCE.md#recordings-context-store-search) |
| Conferences | [List](./REFERENCE.md#conferences-list), [Get](./REFERENCE.md#conferences-get), [Context Store Search](./REFERENCE.md#conferences-context-store-search) |
| Usage Records | [List](./REFERENCE.md#usage-records-list), [Context Store Search](./REFERENCE.md#usage-records-context-store-search) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Context Store Search](./REFERENCE.md#addresses-context-store-search) |
| Queues | [List](./REFERENCE.md#queues-list), [Get](./REFERENCE.md#queues-get), [Context Store Search](./REFERENCE.md#queues-context-store-search) |
| Transcriptions | [List](./REFERENCE.md#transcriptions-list), [Get](./REFERENCE.md#transcriptions-get), [Context Store Search](./REFERENCE.md#transcriptions-context-store-search) |
| Outgoing Caller Ids | [List](./REFERENCE.md#outgoing-caller-ids-list), [Get](./REFERENCE.md#outgoing-caller-ids-get), [Context Store Search](./REFERENCE.md#outgoing-caller-ids-context-store-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Twilio API docs

See the official [Twilio API reference](https://www.twilio.com/docs/usage/api).

## Version information

- **Package version:** 1.0.4
- **Connector version:** 1.0.4
- **Generated with Connector SDK commit SHA:** unknown