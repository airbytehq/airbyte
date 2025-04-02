---
products: all
---

# API documentation

The Airbyte API provides a way for developers to programmatically interact with Airbyte. It is available for all Airbyte products: Airbyte OSS, Cloud & Self-Hosted Enterprise.

Our API is a reliable, easy-to-use interface for programmatically controlling the Airbyte platform. It can be extended to:

- Enable users to control Airbyte programmatically and use with Orchestration tools (ex: Airflow)
- Enable [Airbyte Embedded](https://airbyte.com/ai)

## Configuring API Access

View our documentation [here](./using-airbyte/configuring-api-access.md) to learn how to start using the Airbyte API.

## Using the Airbyte API

Navigate to our full API documentation to learn how to retrieve your access token, make API requests, and manage resources like sources, destinations, and workspaces.

Our full API documentation is located here: [reference.airbyte.com](https://reference.airbyte.com/reference/getting-started).

:::note
Only for OSS users, to access the API in the OSS edition, you need to use the `/api/public/v1` path prefix. (ex: retrieve list of workspaces with `curl http://localhost:8000/api/public/v1/workspaces`)
:::

## Configuration API (Deprecated)

The configuration API is now deprecated and no longer supported. It is an internal API that is designed for communications between different Airbyte components ratther than managing your Airbyte workspace.

Users utilize the Config API at their own risk. This API is utilized internally by the Airbyte Engineering team and may be modified in the future if the need arises.
