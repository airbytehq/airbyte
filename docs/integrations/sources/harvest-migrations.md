# Harvest Migration Guide

## Upgrading to 1.0.0

This update results in a change the following streams, requiring reset:
- `expenses_clients`
- `expenses_categories`
- `expenses_projects`
- `expenses_team`
- `time_clients`
- `time_projects`
- `time_tasks`
- `time_team`
- `uninvoiced`
- `estimate_messages`
- `invoice_payments`
- `invoice_messages`
- `project_assignments`

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning Source Harvest from the Python Connector Development Kit (CDK) to our new low-code framework improving maintainability and reliability of the connector. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

## Steps to Reset Streams

To reset your data for the impacted streams, follow the steps below:

1. Select **Connections** in the main nav bar.
    1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
    1. In the **Enabled streams** list, click the three dots on the right side of the stream requiring reset and select **Reset this stream**.

A fresh sync will run for the stream. For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
