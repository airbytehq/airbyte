# On Running a Sync

## One of your sync jobs is failing

Several things to check:

* **Is Airbyte updated to your latest version?** You can see the latest version [here](https://github.com/airbytehq/airbyte/tags). If not, please upgrade to the latest one
* **Is the connector that is failing updated to the latest version?** You can check the latest version available for the connectors [in the yamls here](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed). If you don't have the latest connector version, make sure you first update to the latest Airbyte version, and then go to the Admin section in the web app and put the right version in the cell for the connector. Then try again.

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

## Your incremental connection is not working

Our current version of incremental is [append](../understanding-airbyte/connections/incremental-append.md). It works from a cursor field. So you need to check which cursor field you're using and if it's well populated in every record in your table.

If this is true, then, there are still several things to check:

* **Is Airbyte updated to your latest version?** You can see the latest version [here](https://github.com/airbytehq/airbyte/tags). If not, please upgrade to the latest one
* **Is the connector that is failing updated to the latest version?** You can check the latest version available for the connectors [in the yamls here](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed). If you don't have the latest connector version, make sure you first update to the latest Airbyte version, and then go to the Admin section in the web app and put the right version in the cell for the connector. Then try again.

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

## Airbyte says successful sync, but some records are missing

Several things to check:

* What is the name of the table you are looking at in the destination? Let's make sure you're not looking at a temporary table.
* **Is the basic normalization toggle set to true at the connection settings?** If it's false, you won't see columns but most probably a JSON file. So you need to switch it on true, and try again.
* **Is Airbyte updated to your latest version?** You can see the latest version [here](https://github.com/airbytehq/airbyte/tags). If not, please upgrade to the latest one
* **Is the connector that is failing updated to the latest version?** You can check the latest version available for the connectors [in the yamls here](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed). If you don't have the latest connector version, make sure you first update to the latest Airbyte version, and then go to the Admin section in the web app and put the right version in the cell for the connector. Then try again.

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

