---
sidebar_label: "Pydantic AI"
sidebar_position: 1
---

# Agent connector tutorial: Pydantic AI

In this tutorial, you'll create a new Python project with uv, add a Pydantic AI agent, equip it with one of Airbyte's agent connectors, and use natural language to explore your data. This tutorial uses GitHub, but if you don't have a GitHub account you can swap in any other agent connector and perform different operations.

Your agent executes through Airbyte. Airbyte Agents owns the OAuth apps, stores your third-party tokens, and refreshes them for you. Your Python code only ever sees your Airbyte client ID and client secret.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AI tools. You can complete it in about 15 minutes.

The tutorial assumes you have basic knowledge of the following tools, but most software engineers shouldn't struggle with anything that follows.

- Python and package management with uv
- Pydantic AI
- GitHub, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.13 or later
- [uv](https://github.com/astral-sh/uv)
- An [Airbyte Agents account](https://app.airbyte.ai). You can sign up for free.
- Your Airbyte API credentials. Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app. See [Manage your user profile](../../admin/profile) for details.
- A GitHub connector added to your Airbyte Agents workspace. Add one of these two ways:
    - **Web app (recommended)**: Go to [Credentials](https://app.airbyte.ai/credentials) in the Airbyte Agents web app, add a GitHub connector, and authenticate it with a [GitHub personal access token](https://github.com/settings/tokens) (a classic token with `repo` scope is sufficient for this tutorial) or OAuth. See [Add a connector](../../interfaces/ui/add-connector) for details.
    - **API**: Create a connector with `POST /api/v1/integrations/connectors` and store your GitHub credentials. See [Add a connector](../../interfaces/api/add-connector) for details.
- An [OpenAI API key](https://platform.openai.com/api-keys). This tutorial uses OpenAI, but Pydantic AI supports other LLM providers if you prefer.

## Part 1: Create a new Python project

In this tutorial you initialize a basic Python project to work in. However, if you have an existing project you want to work with, feel free to use that instead.

Create a new project using uv:

```bash
uv init my-ai-agent --app
cd my-ai-agent
```

This creates a project with the following structure:

```text
my-ai-agent/
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
└── README.md
```

You create `.env` and `uv.lock` files in later steps, so don't worry about them yet.

## Part 2: Install dependencies

Install the Airbyte agent SDK, Pydantic AI, and `python-dotenv`:

```bash
uv add airbyte-agent-sdk pydantic-ai python-dotenv
```

This command installs:

- `airbyte-agent-sdk`: The Airbyte Agents Python SDK, which ships every connector as a typed submodule.
- `pydantic-ai`: The AI agent framework, which includes support for multiple LLM providers including OpenAI, Anthropic, and Google.
- `python-dotenv`: A library you can use to load environment variables from a `.env` file.

:::note
If you want a smaller installation with only OpenAI support, you can use `pydantic-ai-slim[openai]` instead of `pydantic-ai`. See the [Pydantic AI installation docs](https://ai.pydantic.dev/install/) for more options.
:::

## Part 3: Import Pydantic AI and the GitHub agent connector

1. Create an `agent.py` file for your agent definition:

    ```bash
    touch agent.py
    ```

2. Add the following imports to `agent.py`:

    ```python title="agent.py"
    from dotenv import load_dotenv
    from pydantic_ai import Agent
    from airbyte_agent_sdk import connect
    from airbyte_agent_sdk.connectors.github import GithubConnector
    ```

    These imports provide:

    - `load_dotenv`: Load environment variables from your `.env` file.
    - `Agent`: The Pydantic AI agent class that orchestrates LLM interactions and tool calls.
    - `connect`: The Airbyte agent SDK entry point. One call returns a typed connector bound to your workspace.
    - `GithubConnector`: The connector class. You reference it when decorating the tool so the SDK can describe the connector's entities and actions to the agent.

## Part 4: Add a .env file with your secrets

1. Create a `.env` file in your project root and add your secrets to it. Replace the placeholder values with your actual credentials.

    ```text title=".env"
    AIRBYTE_CLIENT_ID=your-airbyte-client-id
    AIRBYTE_CLIENT_SECRET=your-airbyte-client-secret
    OPENAI_API_KEY=your-openai-api-key
    ```

    Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app.

    :::warning
    Never commit your `.env` file to version control. If you do this by mistake, rotate your secrets immediately.
    :::

2. Add the following line to `agent.py` after your imports to load the environment variables:

    ```python title="agent.py"
    load_dotenv()
    ```

    This makes your secrets available via `os.environ`. Pydantic AI automatically reads `OPENAI_API_KEY` from the environment, and the agent SDK picks up `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the environment in the next step.

## Part 5: Configure your connector and agent

Now that your environment is set up, add the following code to `agent.py` to create the GitHub connector and Pydantic AI agent.

### Define the connector

Connect to GitHub through your Airbyte Agents workspace:

```python title="agent.py"
github = connect("github")
```

One line does four things for you:

- Reads `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the environment.
- Defaults to the `"default"` workspace, which is where the web app stores credentials unless you change it.
- Returns a typed `GithubConnector` bound to the authenticated GitHub connector you added earlier.
- Routes every `github.execute(...)` call through Airbyte's hosted API, which holds the GitHub OAuth tokens and refreshes them for you.

You never register an OAuth app, copy a GitHub token into your code, or write token-refresh logic.

If you want to connect to a different workspace or pass credentials explicitly, use `connect("github", workspace_name="my-workspace", client_id=..., client_secret=...)` or pass an `AirbyteAuthConfig`. See the [SDK reference](https://github.com/airbytehq/airbyte-agent-sdk) for details.

### Define the agent

Create a Pydantic AI agent with a system prompt that describes its purpose:

```python title="agent.py"
agent = Agent(
    "openai:gpt-4o",
    system_prompt=(
        "You are a helpful assistant that can access GitHub data through the "
        "github_execute tool. Be concise and accurate."
    ),
)
```

- The `"openai:gpt-4o"` string specifies the model to use. You can use a different model by changing the model string. For example, use `"openai:gpt-4o-mini"` to lower costs, or see the [Pydantic AI models documentation](https://ai.pydantic.dev/models/) for other providers like Anthropic or Google.
- The `system_prompt` parameter is where you encode any API idiosyncrasies the model can't see in the tool schema. The Airbyte agent SDK already exposes entity names, actions, and enum values through the tool description, so the prompt only needs to carry domain constraints (pagination defaults, date formats, preferred streams) as your agent grows.
- The prompt references a `github_execute` tool. You register that tool in the next part.

## Part 6: Add a tool to your agent

Rather than one tool per GitHub endpoint, the Airbyte agent SDK exposes the entire GitHub API through a single `execute(entity, action, params)` entry point. The `tool_utils` decorator fills in the entity and action catalog as the tool description, so the model knows what's available without you writing a schema.

Add the following to `agent.py`:

```python title="agent.py"
@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await github.execute(entity, action, params or {})
```

The decorator stack is the whole tool definition. No per-action `docstring`, no `GITHUB_LIST_COMMITS` or `GITHUB_GET_PR` sprawl, one entry point that covers the full connector. `@GithubConnector.tool_utils` appends the full entity and action catalog to the tool description, and caps oversized responses. As the connector grows, the tool signature stays the same.

Each `execute` call returns a structured result with `data` (the records) and `meta` (pagination cursors). Pydantic AI serializes the dict for the model automatically, so you don't need to call `json.dumps` here. You can keep the result as-is, filter it in Python, or page through it using `meta.end_cursor`.

## Part 7: Run your project

Now that your agent is configured with a tool, update `main.py` and run your project.

1. Update `main.py`. This code creates a simple chat interface in your command line tool and allows your agent to remember your conversation history between prompts.

    ```python title="main.py"
    import asyncio
    from agent import agent

    async def main():
        print("GitHub Agent Ready! Ask questions about GitHub repositories.")
        print("Type 'quit' to exit.\n")

        history = None

        while True:
            prompt = input("You: ")
            if prompt.lower() in ('quit', 'exit', 'q'):
                break
            result = await agent.run(prompt, message_history=history)
            history = result.all_messages()
            print(f"\nAgent: {result.output}\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

2. Run the project.

    ```bash
    uv run main.py
    ```

### Chat with your agent

The agent waits for your input. Once you prompt it, the agent decides which entity and action to call based on your question, asks Airbyte to execute it, and returns a natural language response. Try prompts like:

- "List the 10 most recent open issues in airbytehq/airbyte"
- "What are the 10 most recent pull requests that are still open in airbytehq/airbyte?"
- "Are there any open issues that might be fixed by a pending PR?"

The agent has basic message history within each session, and you can ask followup questions based on its responses.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **HTTP 401/403 errors from Airbyte**: Verify that `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` are copied correctly from your [Profile page](https://app.airbyte.ai/profile).
- **"No connector found" or "connector not configured"**: Make sure you've added a GitHub connector in the [Credentials](https://app.airbyte.ai/credentials) page of the Airbyte Agents web app. `connect("github")` defaults to the `"default"` workspace; if you added the connector to a different workspace, pass `workspace_name="your-workspace-name"` to `connect()`.
- **HTTP 401/403 errors from GitHub**: The GitHub token or OAuth credentials stored in your connector are invalid or missing required scopes. Open your GitHub connector in the web app and reauthenticate with a valid token that has `repo` scope.
- **Empty `data=[]` responses from filtered queries**: Most GitHub filters use case-sensitive values. Confirm the agent is sending uppercase values (for example, `states=["OPEN"]` rather than `states=["open"]`). The system prompt in this tutorial nudges the model to do that by default.
- **OpenAI errors**: Verify your `OPENAI_API_KEY` is valid, has available credits, and won't exceed rate limits.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add Pydantic AI and Airbyte's GitHub agent connector to your project
- Configure environment variables for your Airbyte Agents credentials
- Register a single tool that covers the entire GitHub API
- Run your project and use natural language to interact with GitHub data through Airbyte

## Next steps

- **Add another connector.** The same `connect(...)` + `execute(...)` pattern covers the full [Airbyte agent connectors catalog](../../connectors). Add Slack, Stripe, Salesforce, or any other connector in the web app, then call `slack = connect("slack")` in your agent and register a second tool with another `@agent.tool_plain` / `@SlackConnector.tool_utils` stack. Your agent now reads GitHub and posts to Slack with no additional OAuth setup.
- **Use write actions.** Connectors expose create, update, and post actions alongside the read ones. Ask the agent to file an issue, comment on a PR, or send a Slack message, and `execute` carries the write through with the stored OAuth token.
- **Let your AI assistant scaffold the next agent.** The Airbyte agent SDK ships skills for Claude Code and Codex that carry the patterns above, so you can ask your assistant to build a new agent without retyping them. See the [airbyte-agent-sdk repository](https://github.com/airbytehq/airbyte-agent-sdk) for installation instructions.
- **Reach the same connectors from any MCP client.** Airbyte Agents exposes the same connectors through a hosted MCP endpoint that works with Claude Code, Cursor, and ChatGPT. See the [FastMCP tutorial](./tutorial-fastmcp) for a local-server variant you can run yourself.
