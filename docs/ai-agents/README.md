---
products: embedded
---

# AI Agents
Airbyte provides multiple tools to help you build data applications.

- **Airbyte Embedded Widget**: App development teams who have signed up for Airbyte Embedded and are looking to get started onboarding customers using the Embedded Widget can follow the get started guide at the bottom of this page, which will step you through a complete sample onboarding app.
- **MCP Server**: App developers looking to utilize PyAirbyte to generate pipelines in code can follow the steps below to utilize the PyAirbyte MCP server. 
- **Authentication Proxies**: Connect safely to 3rd party APIs using Airbyte's Authentication Proxies.


## Prerequisites

Before using any Airbyte developer tools, ensure you have:

- **Airbyte Cloud account**: Sign up at [cloud.airbyte.com](https://cloud.airbyte.com)
- **Embedded access**: Contact michel@airbyte.io or teo@airbyte.io to enable Airbyte Embedded on your account
- **API credentials**: Available in your Airbyte Cloud dashboard under Settings > Applications

## Airbyte Embedded

[Airbyte Embedded](https://airbyte.com/embedded) equips product and software teams with the tools needed to move customer data and deliver context to AI applications.

### Embedded Workspaces & Widget

Airbyte Embedded creates isolated workspaces for each of your customers, allowing them to configure their own data sources while keeping their data separate and secure. The Embedded Widget provides a pre-built UI component that handles the entire user onboarding flow, from authentication to source configuration.

:::info
Currently, S3 is the only supported destination for Airbyte Embedded. Additional destinations will be supported in the future.
:::

Once your Organization is enabled via Airbyte Embedded, you can begin onboarding customers via the Embedded Widget. You can download the code for the onboarding app [via GitHub](https://github.com/airbytehq/embedded-demoapp).


## PyAirbyte MCP

[The PyAirbyte remote MCP server](./pyairbyte-mcp/README.md) provides the ability for application developers to generate a data pipeline in Python using a single prompt. It is currently designed to work within Cursor, with broader support coming in the near future.

## Proxy Requests

### API Sources
:::warning
The Airbyte Proxy feature is in alpha, which means it is still in active development and may include backward-incompatible changes. [Share feedback and requests directly with us](mailto:sonar@airbyte.io).
:::

Airbyte's Authentication Proxy enables you to submit authenticated requests to external APIs. It can be both to fetch and write data.

Here's an example of how to query an external API with the proxy:

```bash
curl -X POST -H 'Content-Type: application/json' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
-d {"method": "GET", "url": "https://api.stripe.com/v1/balance", "headers": {"additional_header_key": "value"}}' \
'https://api.airbyte.ai/api/v1/sonar/apis/{SOURCE_ID}/request'
```

Here's an example of a POST:

```bash
curl -X POST -H 'Content-Type: application/json' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
-d {"method": "POST", "url": "https://api.stripe.com/v1/balance", "body": {"key": "value"}}' \
'https://api.airbyte.ai/api/v1/sonar/apis/{SOURCE_ID}/request'
```

Airbyte's Authentication Proxy can be used to authenticate using a Source configured through the Widget.

The following integrations are currently supported. More will follow shortly:
- Stripe

### File Storage Sources

Airbyte's File Storage Proxy enables you to submit authenticated requests to file storage sources. It can be used to list or fetch files.

Here's an example of how to list files:
```bash
curl -X GET -H 'Content-Type: application/json' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
'https://api.airbyte.ai/api/v1/sonar/files/{SOURCE_ID}/list/path/to/directory/or/file/prefix'
```

Here's an example of how to fetch a file:
```bash
curl -X GET -H 'Content-Type: application/octet-stream' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
-H 'Range: bytes=0-1048575' \
'https://api.airbyte.ai/api/v1/sonar/files/{SOURCE_ID}/get/path/to/file'
```

For small files, you may omit the `Range` header.

The following integrations are currently supported. More will follow shortly:
- S3
