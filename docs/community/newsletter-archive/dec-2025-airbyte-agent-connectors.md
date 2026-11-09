---
sidebar_label: "Dec 2025: Launching Agent connectors!"
---
# Launching Agent connectors!

_Published December 16, 2025._

![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/dec-2025-airbyte-agent-connectors/octavia-hand-banner-8d48dd08c6.jpg)

As part of our ongoing work to make agentic systems truly production-ready, Agent Connectors are now available for teams building with agents.

## Airbyte Agent Connectors

[![Airbyte Agent Connectors](https://airbyte.com/images/community/newsletter/bodies/external/dec-2025-airbyte-agent-connectors/introducing-airbyte-agentic-1-01kc7z2ynd0xdq7f9zxsatsqc5-acbb72a291.jpg)](https://github.com/airbytehq/airbyte-agent-connectors/)

Airbyte Agent Connectors give AI agents consistent, real-time access to the operational data they need for context-rich decision making.

The first set of connectors is available now with coverage for **Gong, Zendesk Support, GitHub, HubSpot, Salesforce, Jira, Asana, Stripe, Greenhouse and Linear**. Each Connector is a stand-alone Python package that you can use directly in your app, plug into an agent framework, or expose through [MCP](https://github.com/airbytehq/airbyte-agent-connectors/tree/main/airbyte-agent-mcp) (coming soon).

Airbyte Agent Connectors provide:

- Strongly typed request and response models
- Schema validation + predictable error handling
- Real-time fetch, search, and action operations
- A uniform interface across major SaaS APIs

## Start Building Today

- If you like what we built, please give us a star on our [GitHub Repo](https://github.com/airbytehq/airbyte-agent-connectors).
- We're also launching a [private beta](https://forms.default.com/637248) of our new Agent Data Platform. Let us know if you're interested in joining.
- Check out our [announcement blog](https://airbyte.com/blog/agent-connectors) for more details.

## AI-Assisted Connector Configuration

![AI-Assisted Connector Configuration](https://airbyte.com/images/community/newsletter/bodies/external/dec-2025-airbyte-agent-connectors/component-6-e85da39ef7.png)

Connector setup can be challenging for users, especially with new data sources. That's why we're making it dramatically easier.

Introducing **AI-Assisted Connector Configuration**, a guided, chat-based setup experience that replaces overwhelming documentation with clear, step-by-step interaction. Instead of navigating complex forms alone, users now receive real-time, context-aware guidance from an LLM that understands connector requirements and helps avoid common setup errors.

Here's what the new experience unlocks:

- A chat interface that walks you through the connector setup one instruction at a time
- Automatic validation of values that don't match expected formats (e.g., malformed Snowflake hostnames)
- Credential-safe input handling with clear visual cues
- Optional fields summarized only after all required fields are complete
- Automatic form-view population as the AI fills fields on your behalf
- Clear error summaries if CHECK fails, along with full logs and a suggestion to pivot back to form view

![AI-Assisted Connector Configuration screenshot](https://airbyte.com/images/community/newsletter/bodies/external/dec-2025-airbyte-agent-connectors/screenshot-2025-12-11-at-9-33-06-am-01kca8xw33sjpzdvk8d7wawfys-e223da794d.png)

Try the New AI Setup Flow within your Airbyte workspaces. Available Now!

## Community Updates

![Airbyte Community](https://airbyte.com/images/community/newsletter/bodies/external/dec-2025-airbyte-agent-connectors/octavia-community-9ed528bf96.png)

With the rapid growth of Agentic system builders in our ecosystem, we're restructuring our Slack channels to make it easier to find help, share ideas, and connect with the right people.

We now support three major personas inside our community:

- Data engineering users (OSS, Cloud, connectors)
- AI + agent developers
- MCP connector + agent tooling builders

To better serve them without increasing operational overhead, we're updating the Slack layout. You will see newly added channels for Airbyte's agent connectors (prefixed with #agent-). We have also consolidated/renamed existing channels to keep the navigation simple. You will notice a prefix (#replication-) for the data replication platform you already know and love.

## Join the Community & Meet Other AI Builders on [Slack](https://join.slack.com/t/airbytehq/shared_invite/zt-497lmcwfo-rVj8NkG94vnVZV9H6wIkkg)

## Thank You for Being Part of the Airbyte Community

![Thank You for Being Part of the Airbyte Community](https://airbyte.com/images/community/newsletter/bodies/external/dec-2025-airbyte-agent-connectors/octavia-thankyou-banner-1bf4b0f8c6.jpg)

We're excited to see what you build with Airbyte Agent Connectors, from agent workflows to autonomous pipelines to fully automated business processes. This is just the beginning of a major leap forward in open, governable agentic systems.

As always, we'd love to hear your feedback and see what you are experimenting with. And please don't forget to give us a star on our [airbyte-agent-connector](https://github.com/airbytehq/airbyte-agent-connectors) repo.
