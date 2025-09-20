# Zendesk Support Migration Guide

## Upgrading to 4.0.0

The pagination strategy has been changed from `Offset` to `Cursor-Based`. It is necessary to reset the stream.

### Connector upgrade guide

[Help with upgrades](/platform/managing-airbyte/connector-updates).

### Refresh affected schemas and data

1. Select **Connections** in the main nav bar.
    - Select the connection(s) affected by the update.
2. Select the **Replication** tab.
    - Select **Refresh source schema**.
    - Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page.
    - Ensure the **Refresh affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to refresh your data. See below.
:::

4. Select **Save connection**.

:::note
This will refresh the data in your destination and initiate a fresh sync.
:::

For more information on refreshes your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/refreshes).

## Upgrading to 3.0.0

`cursor_field` for `TicketsMetric` stream is changed to `generated_timestamp`. It is necessary to refresh the data and schema for the affected stream.

### Schema Changes - Added Field

| Stream Name        | Added Fields            |
| -------------------|------------------------ |
| `TicketMetrics`    | `generated_timestamp`   |

## Connector upgrade guide

[Help with upgrades](/platform/managing-airbyte/connector-updates).

### Refresh affected schemas and data

1. Select **Connections** in the main nav bar.
    - Select the connection(s) affected by the update.
2. Select the **Replication** tab.
    - Select **Refresh source schema**.
    - Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page.
    - Ensure the **Refresh affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to refresh your data. See below.
:::

4. Select **Save connection**.

:::note
This will refresh the data in your destination and initiate a fresh sync.
:::

For more information on refreshes your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/refreshes).


## Upgrading to 2.0.0

Stream `Deleted Tickets` is removed. You may need to refresh the connection schema (skipping the data clearing), and running a sync. Alternatively, you can clear your data.

## Upgrading to 1.0.0

`cursor_field` for `Tickets` stream is changed to `generated_timestamp`.
For a smooth migration, you should refresh your stream. Alternatively, you can clear your data.
