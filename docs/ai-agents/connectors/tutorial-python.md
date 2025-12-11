---
sidebar_label: "Python SDK tutorial"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Get started with direct connectors: Python SDK

In this tutorial, you'll create a new Python project, install and run a Pydantic AI agent with one of Airbyte's direct connectors, and learn to use natural language to explore your data. This tutorial uses GitHub, but if you don't have a GitHub account, you can use one of Airbyte's other direct connectors and perform different operations.

Using the Python SDK is more time-consuming than the Connector MCP server, but affords you the most control over how you use direct connectors.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AIs. It assumes you have basic knowledge of the following.

- Python
- Pydantic AI
- GitHub, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.10 or later
- [uv](https://github.com/astral-sh/uv)
- A [GitHub personal access token](https://github.com/settings/tokens). For this tutorial, a classic token with `repo` scope is sufficient.
- An [OpenAI API key](https://platform.openai.com/api-keys). This tutorial uses OpenAI, but Pydantic AI supports other LLM providers.

## Create a new Python project

For simplicity, in this tutorial you scaffold a basic Python project to work in. However, if you have an existing project you want to work with, feel free to use that instead.

1. Create a new project using uv:

   ```bash
   uv init my-ai-agent --app
   cd my-ai-agent
   ```

   This creates a project with the following structure:

   ```text
   my-ai-agent/
   ├── .gitignore
   ├── .python-version
   ├── README.md
   ├── main.py
   └── pyproject.toml
   ```

2. Create an `agent.py` file for your agent definition:

   ```bash
   touch agent.py
   ```

By the end of this tutorial, your project will have the following structure:

```text
my-ai-agent/
├── .env
├── .gitignore
├── .python-version
├── README.md
├── agent.py
├── main.py
├── pyproject.toml
└── uv.lock
```

The `.env` file and `uv.lock` file are created in later steps.

## Install dependencies

Install the GitHub connector and Pydantic AI. This tutorial uses OpenAI as the LLM provider, but Pydantic AI supports many other providers.

```bash
uv add airbyte-ai-github pydantic-ai
```

This command installs:

- `airbyte-ai-github`: The Airbyte direct connector for GitHub, which provides type-safe access to GitHub's API.
- `pydantic-ai`: The AI agent framework, which includes support for multiple LLM providers including OpenAI, Anthropic, and Google.

The GitHub connector also includes `python-dotenv`, which you'll use to load environment variables from your `.env` file.

:::note
If you want a smaller installation with only OpenAI support, you can use `pydantic-ai-slim[openai]` instead of `pydantic-ai`. See the [Pydantic AI installation docs](https://ai.pydantic.dev/install/) for more options.
:::

## Import Pydantic AI and the GitHub direct connector

Add the following imports to `agent.py`:

```python title="agent.py"
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from airbyte_ai_github import GithubConnector
from airbyte_ai_github.models import GithubAuthConfig
```

These imports provide:

- `os`: Access environment variables for your GitHub token and LLM API key.
- `load_dotenv`: Load environment variables from your `.env` file.
- `Agent`: The Pydantic AI agent class that orchestrates LLM interactions and tool calls.
- `GithubConnector`: The Airbyte direct connector that provides type-safe access to GitHub's API.
- `GithubAuthConfig`: The authentication configuration for the GitHub connector.

:::note
You'll add more code to `agent.py` in the following sections. The `main.py` file will be updated in the [Run your project](#run-your-project) section.
:::

## Add a .env file with your secret values

Create a `.env` file in your project root to store your API keys:

```text title=".env"
GITHUB_ACCESS_TOKEN=your-github-personal-access-token
OPENAI_API_KEY=your-openai-api-key
```

Replace the placeholder values with your actual credentials.

:::warning
Never commit your `.env` file to version control. The `.gitignore` file created by `uv init` already excludes `.env` files.
:::

Next, add the following line to `agent.py` after your imports to load the environment variables:

```python title="agent.py"
load_dotenv()
```

This makes your secrets available via `os.environ`. Pydantic AI automatically reads `OPENAI_API_KEY` from the environment, and you'll use `os.environ["GITHUB_ACCESS_TOKEN"]` to configure the connector in the next section.

## Configure your GitHub connector and agent

Now that your environment is set up, add the following code to `agent.py` to create the GitHub connector and Pydantic AI agent.

### Define the connector

The GitHub connector authenticates using your personal access token:

```python title="agent.py"
connector = GithubConnector(
    auth_config=GithubAuthConfig(
        access_token=os.environ["GITHUB_ACCESS_TOKEN"]
    )
)
```

### Create the agent

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

The `system_prompt` parameter tells the LLM what role it should play and how to behave. The `"openai:gpt-4o"` string specifies the model to use.

:::note
You can use a different model by changing the model string. For example, use `"openai:gpt-4o-mini"` for lower cost, or see the [Pydantic AI models documentation](https://ai.pydantic.dev/models/) for other providers like Anthropic or Google.
:::

## Verify connector credentials

<!-- Debugging checkpoint before adding tools -->

## Add tools to your agent

### Expose GitHub operations as Pydantic AI tools

<!-- It looks something like this (generic example, not github-specific)

```python title=""
@agent.tool_plain
async def list_users(limit: int = 10):
    return await connector.users.list(limit=limit)

@agent.tool_plain
async def get_user(user_id: str):
    return await connector.users.get(id=user_id)
``` -->

### Add issue management tools

<!-- we use the connector's operations
Options:
issues__list() - Returns a list of issues for the specified repository using GraphQL
issues__get() - Gets information about a specific issue using GraphQL
issues__search() - Search for issues using GitHub's search syntax

 -->

### Add pull request management tools

<!-- 
we use the connector's operations
pull_requests__list() - Returns a list of pull requests for the specified repository using GraphQL
pull_requests__get() - Gets information about a specific pull request using GraphQL
pull_requests__search() - Search for pull requests using GitHub's search syntax

 -->

## Run your project

<!-- Define how to invoke the agent and what to expect -->

### Identify open issues that are likely to be resolved by pending PRs based on the issue and PR descriptions

<!-- 

Have a conversation with the LLM

-->

## Summary

In this tutorial, you learned how to:

- Set up a new Python project
- Install Pydantic AI and a direct connector
- Add tools to your agent using your direct connector
- Run your Python project and use natural language to interact with your data

## Next steps

- Continue adding more connectors to your project.
- ???
- Profit
