---
sidebar_position: 3
sidebar_label: Implementation guide
---

# Implementation guide

The [quick starts](../quickstarts/) show you how Agent Engine works. These guides show you how to build with it for your specific use case. They assume you've completed a quick start and have basic knowledge of the platform, but you're starting fresh from your own existing project.

## Which guide is for you?

Agent Engine serves two primary audiences. Your use case determines which architectural patterns, authentication flows, and credential management strategies you need.

### Internal use cases

You're building an agent for your own organization. You control the credentials, and your agent operates on behalf of your team or company. Examples include:

- An internal support bot that queries your CRM and ticketing systems
- An operations agent that monitors sales pipelines and sends Slack alerts
- A research assistant that pulls data from multiple SaaS tools for your team

You don't need to build an authentication flow for end-users. You provide your own API credentials and get to work.

**[Start here: Internal use cases](internal.md)**

### Multi-tenant agentic products

You're building a product where your customers connect their own data sources. Each customer brings their own credentials, and you need to manage them securely at scale. Examples include:

- An AI company selling an agentic CRM assistant where each customer connects their own Salesforce and HubSpot
- A platform that provides AI-powered analytics across customers' own data sources
- A SaaS product with an agent feature that reads from customers' GitHub, Jira, or Slack

You need to build an authentication flow, manage per-customer credentials, and enforce data isolation.

**[Start here: Multi-tenant agentic products](b2b.md)**

### Key differences

| Concern | Internal use cases | Multi-tenant agentic products |
|---|---|---|
| **Customers** | One (or a small handful) | Many, each with their own credentials |
| **Credentials** | You provide them directly | Your end-users provide theirs through an auth flow |
| **Authentication flow** | None needed | Required (Authentication Module or custom OAuth) |
| **Token hierarchy** | Simplified | Full hierarchy (application > scoped > widget) |
| **Primary concern** | Empower agents with tools quickly | Data isolation, multi-tenancy, credential lifecycle |
| **Typical architecture** | Python agent or backend service | Backend service + frontend auth widget |
