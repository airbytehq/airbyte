# Shipstation

<HideInUI>

This page contains the setup guide and reference information for the Shipstation source connector.

</HideInUI>

## Prerequisites

To set up the Shipstation source connector, you will need:

- [Shipstation API Key + API Secret](https://www.shipstation.com/docs/api/requirements/#authentication)


<HideInUI>

## Supported sync modes

The Shipstation source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)

## Supported streams

| Stream                                                                              
|:------------------------------------------------------------------------------------|
| [Accound tags](https://www.shipstation.com/docs/api/accounts/list-tags)             |
| [Carriers](https://www.shipstation.com/docs/api/carriers/list)                      |
| [Packages](https://www.shipstation.com/docs/api/carriers/list-packages)             |
| [Services](https://www.shipstation.com/docs/api/carriers/list-services)             |
| [Customers](https://www.shipstation.com/docs/api/customers/list)                    |
| [Fulfillments](https://www.shipstation.com/docs/api/fulfillments/list-fulfillments) |
| [Orders](https://www.shipstation.com/docs/api/orders/list-orders)                   |
| [Products](https://www.shipstation.com/docs/api/products/list)                      |
| [Shipments](https://www.shipstation.com/docs/api/shipments/list)                    |
| [Stores](https://www.shipstation.com/docs/api/stores/list)                          |
| [Users](https://www.shipstation.com/docs/api/users/list)                            |
| [Warehouses](https://www.shipstation.com/docs/api/warehouses/list)                  |
| [Webhooks](https://www.shipstation.com/docs/api/webhooks/list)                      |


## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about the Shipstation connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

The Shipstation connector should not run into [Shipstation API](https://www.shipstation.com/docs/api/requirements/#api-rate-limits) limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

### Troubleshooting

- Check out common troubleshooting issues for the Instagram source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------
|         |            |    | New Source: Shipstation                                                                                                                        |

</details>

</HideInUI>
