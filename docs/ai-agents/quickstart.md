# Quickstart: Build Your First AI Agent with Airbyte

This quickstart guide will walk you through building your first AI agent with Airbyte Embedded in under 30 minutes. You'll learn how to set up API access, configure a data source, and query data on-demand for your AI application.

## What You'll Build

By the end of this tutorial, you'll have:
- ✅ Airbyte API access configured
- ✅ A workspace and source set up
- ✅ An AI agent that can query real-time data
- ✅ Working code examples in Python and JavaScript

## Prerequisites

Before you begin, ensure you have:

1. **Airbyte Enterprise Account**
   - Self-Managed Enterprise or Airbyte Cloud Enterprise
   - [Contact Sales](https://airbyte.com/company/talk-to-sales) if needed

2. **Development Environment**
   - Python 3.8+ or Node.js 16+
   - Code editor (VS Code, PyCharm, etc.)
   - Terminal/command line access

3. **API Credentials**
   - Client ID and Client Secret (from Airbyte settings)
   - If you don't have these yet, see [Prerequisites](./embedded/prerequisites.md)

## Step 1: Set Up API Access

### 1.1 Install Required Tools

**For Python:**
```bash
pip install requests python-dotenv
```

**For JavaScript:**
```bash
npm install node-fetch dotenv
```

### 1.2 Create Environment File

Create a `.env` file to store your credentials securely:

```bash
# .env
AIRBYTE_CLIENT_ID=your_client_id_here
AIRBYTE_CLIENT_SECRET=your_client_secret_here
AIRBYTE_API_URL=https://api.airbyte.com/v1
```

**Important:** Add `.env` to your `.gitignore` to prevent committing credentials!

### 1.3 Generate Access Token

**Python (`setup.py`):**
```python
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_access_token():
    """Generate Airbyte API access token."""
    url = f"{os.getenv('AIRBYTE_API_URL')}/applications/token"

    response = requests.post(
        url,
        json={
            "client_id": os.getenv("AIRBYTE_CLIENT_ID"),
            "client_secret": os.getenv("AIRBYTE_CLIENT_SECRET")
        }
    )

    response.raise_for_status()
    data = response.json()

    return data["access_token"]

if __name__ == "__main__":
    try:
        token = get_access_token()
        print("✅ Successfully generated access token!")
        print(f"Token: {token[:20]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
```

**JavaScript (`setup.js`):**
```javascript
require('dotenv').config();
const fetch = require('node-fetch');

async function getAccessToken() {
  const url = `${process.env.AIRBYTE_API_URL}/applications/token`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: process.env.AIRBYTE_CLIENT_ID,
      client_secret: process.env.AIRBYTE_CLIENT_SECRET
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.access_token;
}

// Test the function
getAccessToken()
  .then(token => {
    console.log('✅ Successfully generated access token!');
    console.log(`Token: ${token.substring(0, 20)}...`);
  })
  .catch(error => {
    console.error('❌ Error:', error.message);
  });
```

**Run the setup:**
```bash
# Python
python setup.py

# JavaScript
node setup.js
```

**Expected Output:**
```
✅ Successfully generated access token!
Token: eyJ0eXAiOiJKV1QiLCJh...
```

## Step 2: Create a Workspace

Workspaces provide isolation for different customers or environments.

**Python (`create_workspace.py`):**
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    """Generate access token."""
    url = f"{os.getenv('AIRBYTE_API_URL')}/applications/token"
    response = requests.post(url, json={
        "client_id": os.getenv("AIRBYTE_CLIENT_ID"),
        "client_secret": os.getenv("AIRBYTE_CLIENT_SECRET")
    })
    response.raise_for_status()
    return response.json()["access_token"]

def create_workspace(name):
    """Create a new workspace."""
    token = get_access_token()
    url = f"{os.getenv('AIRBYTE_API_URL')}/workspaces"

    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name}
    )

    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    workspace = create_workspace("My AI Agent Workspace")
    print(f"✅ Workspace created!")
    print(f"Workspace ID: {workspace['workspaceId']}")
    print(f"Name: {workspace['name']}")

    # Save workspace ID to .env for future use
    with open('.env', 'a') as f:
        f.write(f"\nAIRBYTE_WORKSPACE_ID={workspace['workspaceId']}\n")
```

**JavaScript (`create_workspace.js`):**
```javascript
require('dotenv').config();
const fetch = require('node-fetch');
const fs = require('fs');

async function getAccessToken() {
  const url = `${process.env.AIRBYTE_API_URL}/applications/token`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: process.env.AIRBYTE_CLIENT_ID,
      client_secret: process.env.AIRBYTE_CLIENT_SECRET
    })
  });

  const data = await response.json();
  return data.access_token;
}

async function createWorkspace(name) {
  const token = await getAccessToken();
  const url = `${process.env.AIRBYTE_API_URL}/workspaces`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Create workspace
createWorkspace('My AI Agent Workspace')
  .then(workspace => {
    console.log('✅ Workspace created!');
    console.log(`Workspace ID: ${workspace.workspaceId}`);
    console.log(`Name: ${workspace.name}`);

    // Append to .env file
    fs.appendFileSync('.env', `\nAIRBYTE_WORKSPACE_ID=${workspace.workspaceId}\n`);
  })
  .catch(error => {
    console.error('❌ Error:', error.message);
  });
```

**Run:**
```bash
# Python
python create_workspace.py

# JavaScript
node create_workspace.js
```

**Expected Output:**
```
✅ Workspace created!
Workspace ID: ws_abc123def456
Name: My AI Agent Workspace
```

## Step 3: Configure a Data Source

For this quickstart, we'll use a public API source. We'll configure a Stripe source as an example.

> **Note:** You'll need Stripe API credentials for this step. You can use Stripe's test mode credentials from your [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys).

**Python (`configure_source.py`):**
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    """Generate access token."""
    url = f"{os.getenv('AIRBYTE_API_URL')}/applications/token"
    response = requests.post(url, json={
        "client_id": os.getenv("AIRBYTE_CLIENT_ID"),
        "client_secret": os.getenv("AIRBYTE_CLIENT_SECRET")
    })
    response.raise_for_status()
    return response.json()["access_token"]

def get_source_definitions(workspace_id):
    """Get available source definitions."""
    token = get_access_token()
    url = f"{os.getenv('AIRBYTE_API_URL')}/workspaces/{workspace_id}/definitions/sources"

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )

    response.raise_for_status()
    return response.json()

def find_stripe_definition(definitions):
    """Find Stripe source definition."""
    for definition in definitions.get('data', []):
        if 'stripe' in definition['name'].lower():
            return definition['sourceDefinitionId']
    return None

def create_source(workspace_id, stripe_api_key):
    """Create a Stripe source."""
    token = get_access_token()
    url = f"{os.getenv('AIRBYTE_API_URL')}/sources"

    # Get Stripe source definition ID
    definitions = get_source_definitions(workspace_id)
    stripe_def_id = find_stripe_definition(definitions)

    if not stripe_def_id:
        raise Exception("Stripe source definition not found")

    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspaceId": workspace_id,
            "name": "Stripe Payments",
            "sourceDefinitionId": stripe_def_id,
            "configuration": {
                "client_secret": stripe_api_key,
                "account_id": "acct_default",
                "start_date": "2024-01-01T00:00:00Z"
            }
        }
    )

    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    workspace_id = os.getenv("AIRBYTE_WORKSPACE_ID")
    stripe_api_key = os.getenv("STRIPE_API_KEY", "sk_test_...")

    if not stripe_api_key.startswith("sk_"):
        print("❌ Please set STRIPE_API_KEY in your .env file")
        exit(1)

    source = create_source(workspace_id, stripe_api_key)
    print(f"✅ Source created!")
    print(f"Source ID: {source['sourceId']}")
    print(f"Name: {source['name']}")

    # Save source ID
    with open('.env', 'a') as f:
        f.write(f"AIRBYTE_SOURCE_ID={source['sourceId']}\n")
```

**Add to your `.env` file:**
```bash
STRIPE_API_KEY=sk_test_your_test_key_here
```

**Run:**
```bash
python configure_source.py
```

**Expected Output:**
```
✅ Source created!
Source ID: src_xyz789abc123
Name: Stripe Payments
```

## Step 4: Query Data with Your AI Agent

Now let's create an AI agent that can query data on-demand!

**Python (`ai_agent.py`):**
```python
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class AirbyteAgent:
    """Simple AI Agent using Airbyte for data access."""

    def __init__(self):
        self.api_url = os.getenv("AIRBYTE_API_URL")
        self.source_id = os.getenv("AIRBYTE_SOURCE_ID")
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        """Generate access token."""
        url = f"{self.api_url}/applications/token"
        response = requests.post(url, json={
            "client_id": os.getenv("AIRBYTE_CLIENT_ID"),
            "client_secret": os.getenv("AIRBYTE_CLIENT_SECRET")
        })
        response.raise_for_status()
        return response.json()["access_token"]

    def query_source(self, stream, filters=None):
        """Query data from configured source."""
        url = f"{self.api_url}/proxy/sources/{self.source_id}/query"

        payload = {"stream": stream}
        if filters:
            payload["filters"] = filters

        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=payload
        )

        response.raise_for_status()
        return response.json()

    def get_recent_charges(self, limit=10):
        """Get recent payment charges."""
        return self.query_source(
            "charges",
            filters={"limit": limit}
        )

    def get_customer_info(self, customer_id):
        """Get specific customer information."""
        return self.query_source(
            "customers",
            filters={"id": customer_id}
        )

    def answer_question(self, question):
        """
        Simple AI agent that answers questions using Airbyte data.
        In a real application, you'd use an LLM here.
        """
        question_lower = question.lower()

        if "recent charge" in question_lower or "latest payment" in question_lower:
            charges = self.get_recent_charges(limit=5)
            if charges.get("records"):
                result = "Here are the recent charges:\n"
                for charge in charges["records"][:5]:
                    amount = charge.get("amount", 0) / 100  # Convert cents to dollars
                    status = charge.get("status", "unknown")
                    result += f"- ${amount:.2f} ({status})\n"
                return result
            else:
                return "No recent charges found."

        elif "customer" in question_lower:
            # Extract customer ID from question (simplified)
            # In real app, use NLP to extract entities
            return "Please provide customer ID to query customer information."

        else:
            return "I can help you with recent charges and customer information. What would you like to know?"

# Example usage
if __name__ == "__main__":
    agent = AirbyteAgent()

    print("🤖 AI Agent initialized with Airbyte data access!\n")

    # Simulate AI agent answering questions
    questions = [
        "What are the recent charges?",
        "Show me the latest payments",
        "Tell me about customer data"
    ]

    for question in questions:
        print(f"❓ Question: {question}")
        answer = agent.answer_question(question)
        print(f"🤖 Answer: {answer}\n")
```

**Run your AI agent:**
```bash
python ai_agent.py
```

**Expected Output:**
```
🤖 AI Agent initialized with Airbyte data access!

❓ Question: What are the recent charges?
🤖 Answer: Here are the recent charges:
- $99.99 (succeeded)
- $149.50 (succeeded)
- $29.99 (succeeded)
- $199.00 (succeeded)
- $49.99 (succeeded)

❓ Question: Show me the latest payments
🤖 Answer: Here are the recent charges:
- $99.99 (succeeded)
- $149.50 (succeeded)
...
```

## Step 5: Add Error Handling and Retry Logic

Let's make our agent more robust:

**Python (`robust_agent.py`):**
```python
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class RobustAirbyteAgent:
    """Production-ready AI Agent with error handling."""

    def __init__(self):
        self.api_url = os.getenv("AIRBYTE_API_URL")
        self.source_id = os.getenv("AIRBYTE_SOURCE_ID")
        self.access_token = None
        self.token_expiry = 0

    def _get_access_token(self, force_refresh=False):
        """Generate or return cached access token."""
        if not force_refresh and self.access_token and time.time() < self.token_expiry:
            return self.access_token

        url = f"{self.api_url}/applications/token"
        response = requests.post(url, json={
            "client_id": os.getenv("AIRBYTE_CLIENT_ID"),
            "client_secret": os.getenv("AIRBYTE_CLIENT_SECRET")
        })

        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]
        # Token expires in 3600 seconds, refresh 5 minutes early
        self.token_expiry = time.time() + data.get("expires_in", 3600) - 300

        return self.access_token

    def query_source(self, stream, filters=None, max_retries=3):
        """Query data with retry logic."""
        url = f"{self.api_url}/proxy/sources/{self.source_id}/query"

        payload = {"stream": stream}
        if filters:
            payload["filters"] = filters

        for attempt in range(max_retries):
            try:
                token = self._get_access_token()
                response = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    json=payload,
                    timeout=30
                )

                if response.status_code == 401:
                    # Token expired, refresh and retry
                    self._get_access_token(force_refresh=True)
                    continue

                if response.status_code == 429:
                    # Rate limited, exponential backoff
                    wait_time = 2 ** attempt
                    print(f"⚠️ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ Timeout. Retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(2 ** attempt)
                else:
                    raise Exception("Request timeout after retries")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Error: {e}. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    raise

        raise Exception("Max retries exceeded")

    def get_recent_charges(self, limit=10):
        """Get recent charges with error handling."""
        try:
            return self.query_source("charges", filters={"limit": limit})
        except Exception as e:
            print(f"❌ Error fetching charges: {e}")
            return {"records": [], "error": str(e)}

# Test robust agent
if __name__ == "__main__":
    agent = RobustAirbyteAgent()

    print("🤖 Robust AI Agent initialized!\n")

    # Test with retries
    result = agent.get_recent_charges(limit=5)

    if result.get("error"):
        print(f"❌ Failed to fetch data: {result['error']}")
    else:
        print(f"✅ Successfully fetched {len(result['records'])} charges")
        for charge in result["records"]:
            amount = charge.get("amount", 0) / 100
            print(f"  - ${amount:.2f}")
```

## Step 6: Integration with LLM (Optional)

Integrate with OpenAI or Anthropic for true AI capabilities:

**Python (`llm_agent.py`):**
```python
import os
from openai import OpenAI
from robust_agent import RobustAirbyteAgent

# Initialize clients
airbyte_agent = RobustAirbyteAgent()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_airbyte_tool(stream, filters=None):
    """Tool for LLM to query Airbyte data."""
    return airbyte_agent.query_source(stream, filters)

# Define tools for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_airbyte",
            "description": "Query data from Airbyte sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "stream": {
                        "type": "string",
                        "description": "The stream to query (e.g., charges, customers)"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filters to apply to the query"
                    }
                },
                "required": ["stream"]
            }
        }
    }
]

def ask_llm_with_data_access(question):
    """Ask LLM a question with access to Airbyte data."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to payment data through Airbyte."},
        {"role": "user", "content": question}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name == "query_airbyte":
                import json
                args = json.loads(tool_call.function.arguments)
                data = query_airbyte_tool(args["stream"], args.get("filters"))
                # Add data to conversation and get final response
                # (simplified - see OpenAI docs for complete implementation)
                return data

    return response.choices[0].message.content

# Example
if __name__ == "__main__":
    answer = ask_llm_with_data_access("What are my recent charges?")
    print(answer)
```

## Next Steps

Congratulations! You've built your first AI agent with Airbyte. Here's what to explore next:

### 1. Explore More Sources
- [Shopify](./proxy-requests/api-sources.md#shopify) for e-commerce data
- [Salesforce](./proxy-requests/api-sources.md#salesforce) for CRM data
- [Google Analytics](./proxy-requests/api-sources.md#google-analytics-4) for web analytics

### 2. Use the Embedded Widget
Instead of building custom UI, use our pre-built widget:
- [Embedded Widget Guide](./embedded/widget/README.md)
- [Widget Integration Tutorial](./embedded/widget/use-embedded.md)

### 3. Implement Advanced Features
- [Connection Templates](./embedded/api/connection-templates.md) for workflow automation
- [Source Templates](./embedded/api/source-templates.md) for user configuration
- [Authentication](./embedded/api/authentication.md) for multi-tenant scenarios

### 4. Production Considerations
- Implement proper error handling and logging
- Add monitoring and observability
- Set up rate limiting and caching
- Implement security best practices

## Troubleshooting

### Issue: "401 Unauthorized" Error
**Solution:** Check that your Client ID and Client Secret are correct and that your token hasn't expired.

### Issue: "403 Forbidden" Error
**Solution:** Verify your account has Enterprise plan access and that source is properly configured.

### Issue: "Source not found" Error
**Solution:** Ensure you've created the source and saved the source ID correctly.

### Issue: "Rate limit exceeded"
**Solution:** Implement exponential backoff retry logic (see Step 5).

## Complete Code Repository

All code examples from this quickstart are available in our GitHub repository:
- [Airbyte AI Agents Examples](https://github.com/airbytehq/ai-agents-examples)

## Additional Resources

- [API Reference](https://reference.airbyte.com)
- [Embedded Widget Documentation](./embedded/widget/README.md)
- [Proxy Requests Guide](./proxy-requests/README.md)
- [Community Forum](https://discuss.airbyte.io)
- [Support](https://airbyte.com/support)

## Get Help

- **Documentation Issues:** [Report on GitHub](https://github.com/airbytehq/airbyte/issues)
- **Technical Support:** [Contact Support](https://airbyte.com/support)
- **Community Chat:** [Join Slack](https://slack.airbyte.io)
