# Devin AI Source

This is the repository for the Devin AI source connector, written in the declarative low-code YAML framework.

## Overview

The Devin AI source connector syncs data from the [Devin AI API (v3)](https://docs.devin.ai/api-reference) to Airbyte. It supports the following streams:

- **Sessions** - Lists all Devin sessions for your organization
- **Session Messages** - Lists all messages in each Devin session conversation (sub-resource of Sessions)
- **Playbooks** - Lists all team playbooks for the organization
- **Secrets** - Lists metadata for all secrets in your organization (no secret values are synced)
- **Knowledge Notes** - Lists all knowledge notes for the organization

## Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `api_token` | string | Yes | Devin API key for authentication (`cog_*` prefix for service users) |
| `org_id` | string | Yes | Your Devin organization ID (`org_*` prefix) |

## Contributing

For general contribution guidelines, see the [Airbyte Contributing Guide](https://docs.airbyte.com/platform/contributing-to-airbyte/).

For connector-specific development, see the [Connector Builder documentation](https://docs.airbyte.com/connector-development/connector-builder-ui/overview).
