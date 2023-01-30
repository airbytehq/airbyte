# Awin

This page contains the setup guide and reference information for the Awin source connector.

This connector supports currently only the [Advertiser API](https://wiki.awin.com/index.php/Advertiser_API). The [Publisher API](https://wiki.awin.com/index.php/Publisher_API) is not yet supported.


## Prerequisites

* A Awin Account with permission to access data from accounts you want to sync.
<!-- env:oss -->
- (Airbyte Open Source) An OAuth2 Token (https://wiki.awin.com/index.php/API_authentication).
<!-- /env:oss -->

## Setup guide

<!-- env:oss -->
**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Awin** from the Source type dropdown.
4. Enter the name for the Awin connector.
5. If you want to synchronize just specific accounts, fill in the comma separated list if accounts you want to synchronize.
6. For **Start Date**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated.
7. For **OAuth2 Token**, fill in your OAuth2 token. Following the [Creating your token](https://wiki.awin.com/index.php/API_authentication) guide to get it.
8. Optionally, define the **Attribution Window** which defines the batch size of days to be downloaded in one API request.
9. Click **Save changes and test**.
<!-- /env:oss -->

## Supported sync modes

The Awin source connector supports the following [sync modes](https://docs.airbyte.com/understanding-airbyte/connections/#sync-modes):

* Full Refresh - Overwrite
<!--
* Full Refresh - Append
* Incremental - Append
* Incremental - Deduped History
-->

## Supported Streams

* [Accounts](https://wiki.awin.com/index.php/API_get_accounts)
* [Publishers](https://wiki.awin.com/index.php/API_get_publishers)
* [Advertiser Transactions](https://wiki.awin.com/index.php/API_get_transactions_list)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                            |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------|
| 0.1.0   | 2023-XX-XX | [21116](https://github.com/airbytehq/airbyte/pull/21116) | Introduce Awin source                              |
