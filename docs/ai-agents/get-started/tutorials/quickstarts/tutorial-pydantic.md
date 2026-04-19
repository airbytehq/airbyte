---
sidebar_label: "Pydantic AI"
sidebar_position: 1
---

# Agent connector tutorial: Pydantic AI

In this tutorial, you'll create a new Python project with uv, add a Pydantic AI agent, equip it with one of Airbyte's agent connectors, and use natural language to explore your data. This tutorial uses GitHub, but if you don't have a GitHub account you can swap in any other agent connector and perform different operations.

Your agent executes through Airbyte, so the third-party credentials you use (for GitHub or any other service) never leave your Airbyte Agents account. Your Python code only ever sees your Airbyte client ID and client secret.

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
- Your Airbyte API credentials. Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app. See [Manage your user profile](../../../admin/profile) for details.
- A GitHub connector added to your Airbyte Agents workspace. Add one of these two ways:
    - **Web app (recommended)**: Go to [Credentials](https://app.airbyte.ai/credentials) in the Airbyte Agents web app, add a GitHub connector, and authenticate it with a [GitHub personal access token](https://github.com/settings/tokens) (a classic token with `repo` scope is sufficient for this tutorial) or OAuth. See [Add a connector](../../../interfaces/ui/add-connector) for details.
    - **API**: Create a connector with `POST /api/v1/integrations/connectors` and store your GitHub credentials. See [Add a connector](../../../interfaces/api/add-connector) for details.
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

Install the GitHub connector and Pydantic AI. This tutorial uses OpenAI as the LLM provider, but Pydantic AI supports many other providers.

```bash
uv add airbyte-agent-sdk pydantic-ai python-dotenv
```

This command installs:

- `airbyte-agent-sdk`: The Airbyte Agents Python SDK, which provides type-safe access to every agent connector.
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
    import os

    from dotenv import load_dotenv
    from pydantic_ai import Agent
    from airbyte_agent_sdk import AirbyteAuthConfig
    from airbyte_agent_sdk.connectors.github import GithubConnector
    ```

    These imports provide:

    - `os`: Access environment variables for your Airbyte and LLM credentials.
    - `load_dotenv`: Load environment variables from your `.env` file.
    - `Agent`: The Pydantic AI agent class that orchestrates LLM interactions and tool calls.
    - `AirbyteAuthConfig`: The auth object that tells the connector which Airbyte workspace and client credentials to use.
    - `GithubConnector`: The Airbyte agent connector that executes GitHub operations through Airbyte Agents.

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

    This makes your secrets available via `os.environ`. Pydantic AI automatically reads `OPENAI_API_KEY` from the environment, and you use `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` to configure the connector in the next section.

## Part 5: Configure your connector and agent

Now that your environment is set up, add the following code to `agent.py` to create the GitHub connector and Pydantic AI agent.

### Define the connector

Define the agent connector for GitHub. It authenticates to Airbyte with your Airbyte client credentials, and Airbyte uses the GitHub credentials you already stored with your connector to talk to GitHub.

```python title="agent.py"
connector = GithubConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="default",
        airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
        airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
    ),
)
```

`workspace_name` is the Airbyte workspace where the SDK looks up your connector. `"default"` points to your Airbyte Agents default workspace, which is where the web app stores credentials unless you change it.

### Define the agent

Create a Pydantic AI agent with a system prompt that describes its purpose:

```python title="agent.py"
agent = Agent(
    "openai:gpt-4o",
    system_prompt=(
        "You are a helpful assistant that can access GitHub repositories, issues, "
        "and pull requests. Use the available tools to answer questions about "
        "GitHub data. Be concise and accurate in your responses."
    ),
)
```

- The `"openai:gpt-4o"` string specifies the model to use. You can use a different model by changing the model string. For example, use `"openai:gpt-4o-mini"` to lower costs, or see the [Pydantic AI models documentation](https://ai.pydantic.dev/models/) for other providers like Anthropic or Google.
- The `system_prompt` parameter tells the LLM what role it should play and how to behave.

## Part 6: Add tools to your agent

Tools let your agent fetch real data from GitHub through Airbyte. Without tools, the agent can only respond based on its training data. By registering connector operations as tools, the agent can decide when to call them based on natural language questions.

Add the following code to `agent.py`.

```python title="agent.py"
@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

The `@GithubConnector.tool_utils` decorator automatically generates a comprehensive tool description from the connector's metadata. This tells the agent what entities are available (issues, pull requests, repositories, etc.), what actions it can perform on each entity, and what parameters each action requires.

With this single tool, your agent can access all of the connector's capabilities. The agent decides which entity and action to use based on your natural language questions.

## Part 7: Run your project

Now that your agent is configured with tools, update `main.py` and run your project.

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
            history = result.all_messages()  # Call the method
            print(f"\nAgent: {result.output}\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

2. Run the project.

    ```bash
    uv run main.py
    ```

### Chat with your agent

The agent waits for your input. Once you prompt it, the agent decides which tools to call based on your question, asks Airbyte to execute them, and returns a natural language response. Try prompts like:

- "List the 10 most recent open issues in airbytehq/airbyte"
- "What are the 10 most recent pull requests that are still open in airbytehq/airbyte?"
- "Are there any open issues that might be fixed by a pending PR?"

The agent has basic message history within each session, and you can ask followup questions based on its responses.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **HTTP 401/403 errors from Airbyte**: Verify that `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` are copied correctly from your [Profile page](https://app.airbyte.ai/profile).
- **"No connector found" or "connector not configured"**: Make sure you've added a GitHub connector in the [Credentials](https://app.airbyte.ai/credentials) page of the Airbyte Agents web app, and that `workspace_name` in your code matches the workspace where you added it (`"default"` if you haven't changed workspaces).
- **HTTP 401/403 errors from GitHub**: The GitHub token or OAuth credentials stored in your connector are invalid or missing required scopes. Open your GitHub connector in the web app and reauthenticate with a valid token that has `repo` scope.
- **OpenAI errors**: Verify your `OPENAI_API_KEY` is valid, has available credits, and won't exceed rate limits.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add Pydantic AI and Airbyte's GitHub agent connector to your project
- Configure environment variables for your Airbyte Agents credentials
- Add tools to your agent using the GitHub connector
- Run your project and use natural language to interact with GitHub data through Airbyte

## Next steps

- Add more agent connectors to your project. Explore other agent connectors in the [Airbyte agent connectors catalog](../../../connectors) to give your agent access to more services like Stripe, HubSpot, and Salesforce. Each connector works the same way: add it in the web app, then initialize it in your code with your Airbyte client credentials.

- Consider how you might like to expand your agent's capabilities. For example, you might want to trigger effects like sending a Slack message or an email based on the agent's findings. You aren't limited to the capabilities of Airbyte's agent connectors. You can use other libraries and integrations to build an increasingly robust agent ecosystem.
