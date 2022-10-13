# Trustpilot

This page guides you through the process of setting up the Trustpilot source connector.

## Prerequisites

- No keys or tokens required

## Set up the Trustpilot source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Token** from the Source type dropdown.
4. Enter a name for your source.
5. For **app_name**, enter the name of the app or company, for which You need reviews from Trustpilot.
6. For **start_date**, enter the start date, from which You want to sync reviews.
7. For **timeout_ms**, enter the timeout in milliseconds between two consequent requests. You won't do it often, because source should work correctly with default timeout and back-off strategy.
8. Click **Set up source**.

## Supported sync modes

The Trustpilot source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

The Trustpilot source connector supports the following streams:

- [Reviews](https://www.trustpilot.com/review/free-now.com) \(Incremental\)

### Data type mapping

The [Trustpilot](https://www.trustpilot.com) uses the same types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions are performed for the Trustpilot connector, but output HTMLs for each Trustpilot website request is parsed internally in connector to get this types.

### Performance considerations

The Trustpilot connector should not run into any limitations under normal usage, but if You're trying to sync too much data, there could be possible back-offs.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                              |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.0  | 2022-10-13 | [17933](https://github.com/airbytehq/airbyte/pull/17933)   | Bump CDK connectors |
