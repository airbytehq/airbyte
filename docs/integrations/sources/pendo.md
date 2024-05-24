# Pendo

Pendo is powerful product analytics tool. The source connector here allows you to fetch data from the v1 API.

Currently, the aggregation endpoint is not supported. Please [create an issue](https://github.com/airbytehq/airbyte/issues/new/choose) if you want more streams supported here.

## Prerequisites

- Created Pendo and enable the integration feature
- Generate [an API token](https://app.pendo.io/admin/integrationkeys)

## Airbyte Open Source

- Api Token

## Airbyte Cloud

- Api Token

## Setup guide

### Create an integration Key In Pendo

1. Login to the Pendo Application as an Admin user.
2. Visit the **Integrations** section in the Pendo App, and then click on **Integration Keys**.
3. Click on the **Add Integration Key** button at the top right-hand side of the screen.
4. Give your new key an appropriate description.
5. If a read-write key is needed, tick the box marked **Allow Write Access**.
6. Click on **Create** to finish.

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Pendo** from the Source type dropdown and enter a name for this connector.
4. Add **API Key** from the last step
5. Click `Set up source`.

### For Airbyte Open Source:

1. Go to the Airbyte you deployed, for example, http://localhost:8000
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Pendo** from the Source type dropdown and enter a name for this connector.
4. Add **API Key** from the last step
5. Click `Set up source`.

## Supported sync modes

The Pendo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh.

## Supported Streams

- [Page](https://engageapi.pendo.io/#a53463f9-bdd3-443e-b22f-b6ea6c7376fb)
- [Feature](https://engageapi.pendo.io/#75c6b443-eb07-4a0c-9e27-6c12ad3dbbc4)
- [Report](https://engageapi.pendo.io/#2ac0699a-b653-4082-be11-563e5c0c9410)
- [Guide](https://engageapi.pendo.io/#4f1e3ca1-fc41-4469-bf4b-da90ee8caf3d)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.5   | 2024-05-20 | [38226](https://github.com/airbytehq/airbyte/pull/38226) | Make connector compatible with the builder                                      |
| 0.1.4   | 2024-04-19 | [37220](https://github.com/airbytehq/airbyte/pull/37220) | Updating to 0.80.0 CDK                                                          |
| 0.1.3   | 2024-04-18 | [37220](https://github.com/airbytehq/airbyte/pull/37220) | Manage dependencies with Poetry.                                                |
| 0.1.2   | 2024-04-15 | [37220](https://github.com/airbytehq/airbyte/pull/37220) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37220](https://github.com/airbytehq/airbyte/pull/37220) | schema descriptions                                                             |
| 0.1.0   | 2023-03-14 | [3563](https://github.com/airbytehq/airbyte/pull/3563)   | Initial Release                                                                 |
