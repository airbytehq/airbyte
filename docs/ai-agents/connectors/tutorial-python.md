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

Before you begin this tutorial, ensure you have installed the following software.

- [Python](https://www.python.org/downloads/) version 3.13.7 or later
- [uv](https://github.com/astral-sh/uv)
- An account with GitHub, or a different third-party [supported by direct connectors](https://github.com/airbytehq/airbyte-ai-connectors/tree/main/connectors).

## Create a new Python project

For simplicity, in this tutorial you scaffold a basic Python project to work in. However, if you have an existing project you want to work with, feel free to use that instead.

## Install the connector

```bash
uv pip install airbyte-ai-github
```

## Import a Pydantic agent and GitHub direct connector

```python title=""
import os
from pydantic_ai import Agent
from airbyte_ai_github import GithubConnector
from airbyte_ai_github.models import GithubAuthConfig
```

## Define your connector

```python title=""
connector = GithubConnector(auth_config=GithubAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
```

## Add a .env file with your secret values for your connector

```text
access_token=x
refresh_token=x
client_id=x
cleint_secret=x
```

## Use the connector

<!-- It looks something like this (generic example, not github-specific)

```python title=""
@agent.tool_plain
async def list_users(limit: int = 10):
    return await connector.users.list(limit=limit)

@agent.tool_plain
async def get_user(user_id: str):
    return await connector.users.get(id=user_id)
``` -->

### GitHub list open issues

<!-- 
Options:
issues__list() - Returns a list of issues for the specified repository using GraphQL
issues__get() - Gets information about a specific issue using GraphQL
issues__search() - Search for issues using GitHub's search syntax

 -->

### Github list unmerged PRs

<!-- 

pull_requests__list() - Returns a list of pull requests for the specified repository using GraphQL
pull_requests__get() - Gets information about a specific pull request using GraphQL
pull_requests__search() - Search for pull requests using GitHub's search syntax

 -->

### Post a message to a Slack channel

<!-- 

Maybe an alert to let a team know that x number of issues can be resolved

-->

## Run your project

### Identify open issues that are likely to be resolved by pending PRs based on the issue and PR descriptions

<!-- 

 -->

### Tell it to post a message to Slack

## Summary

In this tutorial, you learned how to:

- Set up a new Python project
- Install Pydantic AI and a direct connector
- Run your Python project and use natural language to interact with your data

## Next steps

- Continue adding more connectors to your project.
- ???
- Profit
