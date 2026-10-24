---
sidebar_position: 2
sidebar_label: Multi-tenant agentic products
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Implementation guide: Multi-tenant agentic products

This guide walks you through building a multi-tenant integration layer where your customers connect their own data sources. Each customer gets isolated credentials, connectors, and data managed by Agent Engine.

## Overview

This guide is for AI companies building products where end-users bring their own data. Your customers each connect their own GitHub, Salesforce, HubSpot, or other accounts, and your agent operates on their behalf. By the end of this guide, you'll have:

- A token hierarchy that enforces per-customer data isolation
- An authentication flow so your customers can connect their accounts
- Per-customer connector resolution in your agent
- The context store enabled for low-latency search across all customers
- A production-ready multi-tenant architecture

This guide assumes you've completed a [quick start](../quickstarts/) and have basic knowledge of connectors, entities, and actions. You're working from an existing project, not starting from scratch.

## Prerequisites

- An [Agent Engine account](https://app.airbyte.ai/) with your client ID and client secret (find these under **Authentication Module** > **Installation**)
- Python 3.13+ and [uv](https://github.com/astral-sh/uv)
- An LLM provider API key (for example, [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/))
- A frontend where your users can authenticate (or willingness to build one)

## Architecture

In a multi-tenant product, your backend mediates between your frontend, Agent Engine, and your agent. Your customers never interact with Agent Engine directly. Your backend handles token management, and Agent Engine handles credential storage and API execution.

```text
┌──────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│ Your      │───▶│ Your backend │───▶│  Agent Engine    │───▶│ Third-party  │
│ frontend  │    │ (tokens,     │    │  (credentials,  │    │ APIs         │
│           │◀───│  agent)      │◀───│   execution)    │◀───│              │
└──────────┘    └──────────────┘    └─────────────────┘    └──────────────┘
```

The multi-tenancy model has three levels:

- **Organization**: Your Agent Engine account. Contains all your customers.
- **Customer**: An isolated environment for one of your end-users. Holds that user's connectors and credentials.
- **Connector**: A per-customer instance with actual credentials for a specific data source.

Every customer is isolated. A scoped token can only access a single customer. Data never crosses the customer boundary.

## Step 1: Install connector packages

Install the connector packages for the services your product will support. This guide uses GitHub and HubSpot as examples.

```bash
uv add airbyte-agent-github airbyte-agent-hubspot
```

You also need your agent framework:

```bash
uv add pydantic-ai  # or langchain langchain-openai langgraph
```

## Step 2: Enable connectors

Enable every connector your product will offer to customers. This determines which data sources appear in the Authentication Module and which connectors your customers can create.

1. Log in to [Agent Engine](https://app.airbyte.ai/).
2. Click **Connectors** > **Manage Connectors**.
3. Enable each connector your product supports (for example, GitHub, HubSpot, Salesforce, Slack).
4. For each connector, check **Direct** to enable real-time agent queries.

You can also enable connectors via the API. See [Enable a connector](/ai-agents/platform/enable-connector) for details.

## Step 3: Understand the token hierarchy

Agent Engine uses a hierarchical token system to enforce data isolation. Understanding this hierarchy is critical for multi-tenant products.

| Token type | Scope | TTL | Use case |
|---|---|---|---|
| **Application token** | Organization-wide | 15 minutes | Backend operations: managing connectors, listing customers, generating other tokens |
| **Scoped token** | Single customer | 20 minutes | Customer-level operations: creating connectors, executing operations for a specific customer |
| **Widget token** | Single customer + CORS | 20 minutes | Frontend embedding: powering the Authentication Module widget |

**Your backend requests application tokens and generates scoped or widget tokens per-customer. Never expose application tokens to your frontend.**

### Generate tokens

<Tabs>
<TabItem value="python" label="Python" default>

```python title="token_service.py"
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

AIRBYTE_API = "https://api.airbyte.ai/api/v1"
CLIENT_ID = os.environ["AIRBYTE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AIRBYTE_CLIENT_SECRET"]

async def get_application_token() -> str:
    """Get an organization-level application token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AIRBYTE_API}/account/applications/token",
            json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        )
        response.raise_for_status()
        return response.json()["access_token"]

async def get_scoped_token(customer_name: str) -> str:
    """Get a customer-scoped token. Creates the customer if it doesn't exist."""
    app_token = await get_application_token()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AIRBYTE_API}/account/applications/scoped-token",
            headers={"Authorization": f"Bearer {app_token}"},
            json={"customer_name": customer_name},
        )
        response.raise_for_status()
        return response.json()["token"]

async def get_widget_token(customer_name: str, allowed_origin: str) -> str:
    """Get a widget token for embedding the Authentication Module."""
    app_token = await get_application_token()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AIRBYTE_API}/account/applications/widget-token",
            headers={"Authorization": f"Bearer {app_token}"},
            json={
                "customer_name": customer_name,
                "allowed_origin": allowed_origin,
            },
        )
        response.raise_for_status()
        return response.json()["token"]
```

</TabItem>
<TabItem value="api" label="API">

```bash title="Get an application token"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

```bash title="Get a scoped token for a customer"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "customer_acme_corp"
  }'
```

```bash title="Get a widget token for frontend embedding"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/widget-token \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "customer_acme_corp",
    "allowed_origin": "https://yourapp.com"
  }'
```

</TabItem>
</Tabs>

## Step 4: Build your authentication flow

Your customers need a way to connect their accounts. Agent Engine provides three options, listed here in order of recommendation.

### Option 1: Authentication Module (recommended)

The [Authentication Module](/ai-agents/platform/authenticate/build-auth/authentication-module) is a pre-built widget you embed in your frontend. It handles connector selection, credential input, and validation. This is the fastest path to production and requires the least code.

#### Backend: Generate widget tokens

Your backend generates widget tokens for each customer. Never expose your client ID or client secret to the frontend.

<Tabs>
<TabItem value="python" label="Python" default>

```python title="app.py"
from fastapi import FastAPI, Request
from token_service import get_widget_token

app = FastAPI()

@app.post("/api/airbyte/widget-token")
async def create_widget_token(request: Request):
    body = await request.json()
    customer_name = body["customer_name"]  # Your internal user/customer ID
    token = await get_widget_token(
        customer_name=customer_name,
        allowed_origin="https://yourapp.com",  # Must match your frontend origin exactly
    )
    return {"token": token}
```

</TabItem>
<TabItem value="api" label="API">

```bash
curl -X POST https://api.airbyte.ai/api/v1/account/applications/widget-token \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "customer_acme_corp",
    "allowed_origin": "https://yourapp.com"
  }'
```

</TabItem>
</Tabs>

#### Frontend: Embed the widget

Install the Authentication Module widget:

```bash npm2yarn
npm install @airbyte-embedded/airbyte-embedded-widget
```

Embed it in your frontend:

```tsx title="ConnectData.tsx"
import { AirbyteEmbeddedWidget } from "@airbyte-embedded/airbyte-embedded-widget";

async function fetchWidgetToken(customerName: string) {
  const response = await fetch("/api/airbyte/widget-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ customer_name: customerName }),
  });
  return response.json();
}

export const ConnectData: React.FC<{ customerName: string }> = ({ customerName }) => {
  const handleConnect = async () => {
    const { token } = await fetchWidgetToken(customerName);

    const widget = new AirbyteEmbeddedWidget({
      token,
      onEvent: (event) => {
        switch (event.message) {
          case "source_created":
            // The customer's connector is now ready to use.
            // Store the source info and refresh your UI.
            console.log("Connector created:", event.data);
            break;
          case "source_create_error":
            console.error("Connection failed:", event.error);
            break;
        }
      },
    });

    widget.open();
  };

  return <button onClick={handleConnect}>Connect your data</button>;
};
```

When a customer completes authentication, Agent Engine creates a connector in that customer's isolated environment. Your agent can immediately begin executing operations against it.

### Option 2: Custom OAuth flow

If you need custom branding on the OAuth consent screen, your own OAuth app credentials, or specific OAuth scopes, build a [custom OAuth flow](/ai-agents/platform/authenticate/build-auth/build-your-own). This requires more effort but allows full control over the user experience.

### Option 3: Direct credential collection

If the connectors you support use API tokens (not OAuth), you can collect credentials in your own UI and store them via the API:

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "connector_type": "github",
    "customer_name": "customer_acme_corp",
    "replication_config": {
      "repositories": ["acme-corp/main-repo"],
      "credentials": {
        "option_title": "PAT Credentials",
        "personal_access_token": "<customers_github_token>"
      }
    }
  }'
```

This approach bypasses the Authentication Module entirely. It's appropriate when your UI already collects API keys, or for connectors that don't support OAuth.

## Step 5: Manage customers programmatically

Customers are created implicitly when you generate a scoped token with a new `customer_name`. However, you'll also need to list, update, and deactivate customers as part of your product's lifecycle.

**Best practice:** Use your internal customer ID or company name as the `customer_name`. This makes it easy to correlate Agent Engine customers with your own records.

<Tabs>
<TabItem value="python" label="Python" default>

```python title="customer_service.py"
import httpx
from token_service import get_application_token

AIRBYTE_API = "https://api.airbyte.ai/api/v1"

async def list_customers():
    """List all customers in your organization."""
    token = await get_application_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AIRBYTE_API}/workspaces",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

async def deactivate_customer(workspace_id: str):
    """Deactivate a customer. Disables all their connections."""
    token = await get_application_token()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{AIRBYTE_API}/workspaces/{workspace_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "inactive"},
        )
        response.raise_for_status()
        return response.json()
```

</TabItem>
<TabItem value="api" label="API">

```bash title="List customers"
curl https://api.airbyte.ai/api/v1/workspaces \
  -H 'Authorization: Bearer <application_token>'
```

```bash title="Deactivate a customer"
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{"status": "inactive"}'
```

```bash title="Delete a customer and all associated resources"
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <application_token>'
```

</TabItem>
</Tabs>

## Step 6: Connect your agent to customer data

In a multi-tenant product, your agent must resolve connectors per-customer at runtime. Each customer has their own connectors with their own credentials. Your agent uses your Airbyte credentials and the customer's name to scope operations to the right customer.

### Per-customer connector initialization

<Tabs>
<TabItem value="python" label="Python" default>

Use dependency injection to scope connectors to the current customer. This example creates connectors per-request with the customer's identity.

```python title="agent.py"
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_hubspot import HubspotConnector

load_dotenv()

@dataclass
class CustomerDeps:
    """Dependencies scoped to a single customer."""
    customer_name: str
    github: GithubConnector
    hubspot: HubspotConnector

def create_customer_deps(customer_name: str) -> CustomerDeps:
    """Create connectors scoped to a specific customer."""
    config = AirbyteAuthConfig(
        customer_name=customer_name,
        airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
        airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
    )
    return CustomerDeps(
        customer_name=customer_name,
        github=GithubConnector(auth_config=config),
        hubspot=HubspotConnector(auth_config=config),
    )

agent = Agent(
    "openai:gpt-4o",
    deps_type=CustomerDeps,
    system_prompt=(
        "You are a data assistant. Use the available tools to answer questions "
        "about the customer's GitHub repositories and HubSpot CRM data."
    ),
)

@agent.tool
@GithubConnector.tool_utils
async def github_execute(
    ctx: RunContext[CustomerDeps], entity: str, action: str, params: dict | None = None
):
    return await ctx.deps.github.execute(entity, action, params or {})

@agent.tool
@HubspotConnector.tool_utils
async def hubspot_execute(
    ctx: RunContext[CustomerDeps], entity: str, action: str, params: dict | None = None
):
    return await ctx.deps.hubspot.execute(entity, action, params or {})
```

When handling a request, create dependencies for the specific customer:

```python title="app.py"
from fastapi import FastAPI, Request
from agent import agent, create_customer_deps

app = FastAPI()

@app.post("/api/agent/query")
async def query_agent(request: Request):
    body = await request.json()
    customer_name = body["customer_name"]  # From your auth middleware
    prompt = body["prompt"]

    deps = create_customer_deps(customer_name)
    result = await agent.run(prompt, deps=deps)
    return {"response": result.output}
```

</TabItem>
<TabItem value="langchain" label="LangChain">

```python title="agent.py"
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_hubspot import HubspotConnector

load_dotenv()

def create_agent_for_customer(customer_name: str):
    """Create an agent with tools scoped to a specific customer."""
    config = AirbyteAuthConfig(
        customer_name=customer_name,
        airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
        airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
    )

    github = GithubConnector(auth_config=config)
    hubspot = HubspotConnector(auth_config=config)

    @tool
    @GithubConnector.tool_utils
    async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
        """Execute GitHub connector operations."""
        result = await github.execute(entity, action, params or {})
        return json.dumps(result, default=str)

    @tool
    @HubspotConnector.tool_utils
    async def hubspot_execute(entity: str, action: str, params: dict | None = None) -> str:
        """Execute HubSpot connector operations."""
        result = await hubspot.execute(entity, action, params or {})
        return json.dumps(result, default=str)

    llm = ChatOpenAI(model="gpt-4o")
    return create_react_agent(llm, [github_execute, hubspot_execute])
```

</TabItem>
<TabItem value="api" label="API">

When using the API, scope operations to a customer by using their scoped token or by listing their connectors with an application token.

```bash title="List a customer's connectors"
curl https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <scoped_token>'
```

```bash title="Execute an operation on a customer's connector"
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "entity": "contacts",
    "action": "list"
  }'
```

</TabItem>
</Tabs>

## Step 7: Enable the context store

For multi-tenant products, the [context store](/ai-agents/platform/context-store) is especially valuable. It gives every customer's agent access to low-latency search without you building indexing infrastructure per-customer.

1. In Agent Engine, click **Connectors**.
2. Enable **Enable Airbyte-managed Context Store for agent search**.

The context store populates automatically for each customer's connected sources. Each customer's data is isolated and only accessible through their scoped credentials.

Once enabled, the `search` action becomes available on your connectors:

```python
# Searches only within this customer's data
result = await ctx.deps.hubspot.execute("contacts", "search", {
    "query": {"filter": {"eq": {"company": "Acme Corp"}}},
    "limit": 10
})
```

You don't need to change your tool registration. The auto-generated tool descriptions include the `search` action automatically when the context store is active.

## Step 8: Go to production

### Secure your backend

- **Never expose application tokens or client secrets to your frontend.** Use widget tokens for frontend-embedded flows.
- **Validate the `allowed_origin`** when generating widget tokens. This must match your frontend's origin exactly, including the port.
- **Use your auth middleware** to resolve the customer identity before generating scoped tokens. Don't trust customer identifiers from the frontend without verification.

### Handle token expiration

- **Python SDK**: Token refresh is automatic.
- **API**: Application tokens expire after 15 minutes. Scoped tokens expire after 20 minutes. Cache and refresh tokens in your backend before they expire.

```python title="token_cache.py"
import time
from dataclasses import dataclass

@dataclass
class CachedToken:
    token: str
    expires_at: float

class TokenCache:
    def __init__(self):
        self._cache: dict[str, CachedToken] = {}

    async def get_application_token(self) -> str:
        cached = self._cache.get("app_token")
        if cached and cached.expires_at > time.time() + 60:  # 60s buffer
            return cached.token

        token = await _fetch_application_token()  # Your API call
        self._cache["app_token"] = CachedToken(
            token=token,
            expires_at=time.time() + 900,  # 15 minutes
        )
        return token

    async def get_scoped_token(self, customer_name: str) -> str:
        cache_key = f"scoped:{customer_name}"
        cached = self._cache.get(cache_key)
        if cached and cached.expires_at > time.time() + 60:
            return cached.token

        token = await _fetch_scoped_token(customer_name)  # Your API call
        self._cache[cache_key] = CachedToken(
            token=token,
            expires_at=time.time() + 1200,  # 20 minutes
        )
        return token
```

### Customer lifecycle management

Map customer events in your product to Agent Engine operations:

| Your product event | Agent Engine action |
|---|---|
| Customer signs up | Generate scoped token (creates customer implicitly) |
| Customer connects a data source | Authentication Module or API connector creation |
| Customer churns or cancels | Set customer status to `inactive` |
| Customer deletes their account | Delete the customer and all associated resources |

### Error handling

In a multi-tenant environment, handle errors per-customer without affecting other customers:

```python
async def safe_execute(connector, entity, action, params=None):
    try:
        return await connector.execute(entity, action, params or {})
    except Exception as e:
        # Log the error with the customer context for debugging.
        # Return a structured error so the agent can respond gracefully.
        return {"error": str(e), "entity": entity, "action": action}
```

### Monitoring

Track per-customer metrics to detect issues early:

- Connector creation success/failure rates
- Operation execution latency per customer
- Token generation and refresh rates
- Authentication Module completion rates

## Best practices summary

- **Use the Authentication Module for your auth flow** unless you have specific branding or OAuth requirements.
- **Use your internal customer ID as the `customer_name`.** This makes correlating Agent Engine data with your own records straightforward.
- **Never expose application tokens to the frontend.** Widget tokens are the only tokens safe for client-side use.
- **Use dependency injection for per-customer connector resolution.** Create dependencies scoped to the customer on each request.
- **Enable the context store.** It provides search capabilities across all customers without per-customer indexing infrastructure.
- **Handle customer lifecycle events.** Map sign-up, churn, and deletion events in your product to the corresponding Agent Engine operations.
- **Use auto-generated tool descriptions.** Override only when the LLM demonstrably misuses a tool.

## Next steps

- Learn about [building custom OAuth flows](/ai-agents/platform/authenticate/build-auth/build-your-own) for custom branding.
- Explore [managing customers](/ai-agents/platform/customers) in detail.
- Browse the [connector catalog](/ai-agents/connectors/) to expand the data sources your product supports.
- Review the [API documentation](/ai-agents/api/) for the complete endpoint reference.
